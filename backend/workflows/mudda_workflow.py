"""
MuddaWorkflow — production-grade Temporal workflow for civic issue resolution.

Determinism Rules (enforced):
    - NO database calls inside this module
    - NO datetime.now() / random / uuid generation
    - NO external API or AI calls
    - ALL side-effects go through Temporal activities
    - Human approval uses Temporal Signals, not activity sleep

State:
    - execution_results: accumulated results from each step
    - ai_context: AI metadata collected from document generation steps
    - approved_steps: signal-driven approval map
"""
from datetime import timedelta
from typing import Any, Dict

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity references
with workflow.unsafe.imports_passed_through():
    from activities.registry import ACTIVITY_REGISTRY
    from activities.execution_tracking_activities import update_execution_status


@workflow.defn
class MuddaWorkflow:
    """
    Main workflow class for executing civic issue resolution plans.

    Stateful: stores execution_results, ai_context, and approved_steps
    across the lifetime of a single workflow execution.
    """

    def __init__(self) -> True:
        self.execution_results: Dict[str, Any] = {}
        self.ai_context: Dict[str, Any] = {}
        self.approved_steps: Dict[str, bool] = {}

    # ------------------------------------------------------------------
    # Signals
    # ------------------------------------------------------------------
    @workflow.signal
    def approve_step(self, step_id: str) -> None:
        """
        Signal handler: mark a step as approved.
        """
        workflow.logger.info("Step approved via signal — step_id=%s", step_id)
        self.approved_steps[step_id] = True

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        """Return the current execution state (safe for external queries)."""
        return {
            "execution_results": self.execution_results,
            "ai_context": self.ai_context,
            "approved_steps": self.approved_steps,
        }

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------
    @workflow.run
    async def run(
        self, workflow_plan: Dict[str, Any], execution_id: str
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow plan composed of activities.

        Args:
            workflow_plan: The workflow plan to execute (contains 'steps' list).
            execution_id: ID of the WorkflowExecution record in the database.

        Returns:
            Final structured result with status and all step results.
        """
        workflow.logger.info(
            "Workflow started — execution_id=%s plan=%s",
            execution_id,
            workflow_plan.get("workflow_name", "Unknown"),
        )

        # Retry policy shared by all activity calls
        retry = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            backoff_coefficient=2.0,
        )

        # ── Mark execution as running ────────────────────────────────
        await workflow.execute_activity(
            update_execution_status,
            args=[{
                "execution_id": execution_id,
                "status": "running",
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        steps = workflow_plan.get("steps", [])

        # ── Execute steps sequentially (DAG order) ───────────────────
        for step in steps:
            step_id: str = step["step_id"]
            activity_id: str = step["activity_id"]
            inputs: Dict[str, Any] = step.get("inputs", {})
            requires_approval: bool = step.get("requires_approval", False)

            workflow.logger.info(
                "Processing step — step_id=%s activity_id=%s approval=%s",
                step_id,
                activity_id,
                requires_approval,
            )

            # ── Human approval (signal-based) ────────────────────────
            if requires_approval:
                workflow.logger.info(
                    "Waiting for approval signal — step_id=%s", step_id
                )
                await workflow.wait_condition(
                    lambda sid=step_id: self.approved_steps.get(sid, False)
                )
                workflow.logger.info("Approval received — step_id=%s", step_id)

            # ── Execute the activity directly ────────────
            try:
                activity_handler = ACTIVITY_REGISTRY.get(activity_id)
                if not activity_handler:
                    raise ValueError(f"Activity '{activity_id}' not found in registry")

                # Resolve template variables in inputs (very basic version)
                # In production, this would be more robust
                resolved_inputs = self._resolve_templates(inputs)

                result = await workflow.execute_activity(
                    activity_handler,
                    args=[resolved_inputs],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=retry,
                )

                # Store results in workflow state
                self.execution_results[step_id] = result
                
                # Update ai_context if relevant
                if isinstance(result, dict) and "ai_metadata" in result:
                    self.ai_context[step_id] = result["ai_metadata"]

                workflow.logger.info(
                    "Step completed — step_id=%s activity=%s",
                    step_id,
                    activity_id,
                )

            except Exception as exc:
                workflow.logger.error(
                    "Step failed — step_id=%s error=%s", step_id, exc
                )

                # Record failure in DB
                await workflow.execute_activity(
                    update_execution_status,
                    args=[{
                        "execution_id": execution_id,
                        "status": "failed",
                        "result_data": {
                            "failed_step": step_id,
                            "error": str(exc),
                            "partial_results": self.execution_results,
                        },
                    }],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry,
                )

                return {
                    "status": "failed",
                    "failed_step": step_id,
                    "reason": str(exc),
                    "partial_results": self.execution_results,
                }

        # ── Mark execution as completed ──────────────────────────────
        await workflow.execute_activity(
            update_execution_status,
            args=[{
                "execution_id": execution_id,
                "status": "completed",
                "result_data": self.execution_results,
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        workflow.logger.info("Workflow completed — execution_id=%s", execution_id)

        return {
            "status": "completed",
            "workflow_name": workflow_plan.get("workflow_name", "Unknown"),
            "results": self.execution_results,
            "ai_context": self.ai_context,
        }

    def _resolve_templates(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic template resolver for activity inputs.
        Supports {{step_id.output_key}} or generic {{key}}.
        """
        resolved = {}
        for k, v in inputs.items():
            if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                path = v[2:-2].strip()
                if "." in path:
                    step_id, key = path.split(".", 1)
                    step_result = self.execution_results.get(step_id, {})
                    if isinstance(step_result, dict):
                        resolved[k] = step_result.get(key, v)
                    else:
                        resolved[k] = v
                else:
                    # Generic input from elsewhere or root level (e.g., issue_id)
                    # For now, searching in all results or keeping as is
                    found = False
                    for result in self.execution_results.values():
                        if isinstance(result, dict) and path in result:
                            resolved[k] = result[path]
                            found = True
                            break
                    if not found:
                        resolved[k] = v
            else:
                resolved[k] = v
        return resolved
