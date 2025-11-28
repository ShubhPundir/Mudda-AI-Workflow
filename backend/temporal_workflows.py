"""
Temporal.io workflow implementations for Mudda AI Workflow system
"""
import os
import asyncio
from datetime import timedelta
from typing import Dict, Any, List
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker
from sqlalchemy.orm import Session
from sessions.database import SessionLocal
from models import Component, WorkflowExecution


class WorkflowActivities:
    """Activities for executing workflow steps"""
    
    @staticmethod
    @activity.defn
    async def execute_component_step(
        component_id: str,
        inputs: Dict[str, Any],
        step_id: str
    ) -> Dict[str, Any]:
        """
        Execute a single component step
        
        Args:
            component_id: ID of the component to execute
            inputs: Input parameters for the component
            step_id: ID of the workflow step
            
        Returns:
            Execution result
        """
        # Get component details from database
        db = SessionLocal()
        try:
            component = db.query(Component).filter(Component.id == component_id).first()
            if not component:
                raise ValueError(f"Component {component_id} not found")
            
            # TODO: Implement actual API call based on component type
            # For now, simulate execution
            result = {
                "step_id": step_id,
                "component_id": component_id,
                "status": "completed",
                "outputs": inputs.get("outputs", []),
                "execution_time": "2024-01-01T00:00:00Z"
            }
            
            return result
            
        finally:
            db.close()
    
    @staticmethod
    @activity.defn
    async def request_human_approval(
        step_id: str,
        approval_data: Dict[str, Any]
    ) -> bool:
        """
        Request human approval for a workflow step
        
        Args:
            step_id: ID of the step requiring approval
            approval_data: Data for the approval request
            
        Returns:
            True if approved, False otherwise
        """
        # TODO: Implement actual approval workflow
        # For now, simulate approval after a delay
        await asyncio.sleep(2)
        return True
    
    @staticmethod
    @activity.defn
    async def update_execution_status(
        execution_id: str,
        status: str,
        result_data: Dict[str, Any] = None
    ):
        """
        Update workflow execution status in database
        
        Args:
            execution_id: ID of the execution
            status: New status
            result_data: Optional result data
        """
        db = SessionLocal()
        try:
            execution = db.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()
            
            if execution:
                execution.status = status
                if result_data:
                    execution.execution_data = result_data
                
                db.commit()
                
        finally:
            db.close()


@workflow.defn
class MuddaWorkflow:
    """Main workflow class for executing civic issue resolution plans"""
    
    def __init__(self):
        self.activities = WorkflowActivities()
    
    @workflow.run
    async def run(self, workflow_plan: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """
        Execute a complete workflow plan
        
        Args:
            workflow_plan: The workflow plan to execute
            execution_id: ID of the execution record
            
        Returns:
            Final execution result
        """
        # Update status to running
        await workflow.execute_activity(
            self.activities.update_execution_status,
            args=[execution_id, "running"],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        steps = workflow_plan.get("steps", [])
        execution_results = {}
        
        # Execute steps in order (following the DAG)
        for step in steps:
            step_id = step["step_id"]
            component_id = step["component_id"]
            inputs = step.get("inputs", {})
            requires_approval = step.get("requires_approval", False)
            
            # Request approval if required
            if requires_approval:
                approved = await workflow.execute_activity(
                    self.activities.request_human_approval,
                    args=[step_id, {"step_id": step_id, "component_id": component_id}],
                    start_to_close_timeout=timedelta(minutes=5)
                )
                
                if not approved:
                    # Update status to failed
                    await workflow.execute_activity(
                        self.activities.update_execution_status,
                        args=[execution_id, "failed", {"error": "Approval denied"}],
                        start_to_close_timeout=timedelta(seconds=30)
                    )
                    return {"status": "failed", "reason": "Approval denied"}
            
            # Execute the step
            try:
                result = await workflow.execute_activity(
                    self.activities.execute_component_step,
                    args=[component_id, inputs, step_id],
                    start_to_close_timeout=timedelta(minutes=10)
                )
                
                execution_results[step_id] = result
                
            except Exception as e:
                # Update status to failed
                await workflow.execute_activity(
                    self.activities.update_execution_status,
                    args=[execution_id, "failed", {"error": str(e)}],
                    start_to_close_timeout=timedelta(seconds=30)
                )
                return {"status": "failed", "reason": str(e)}
        
        # Update status to completed
        await workflow.execute_activity(
            self.activities.update_execution_status,
            args=[execution_id, "completed", execution_results],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        return {
            "status": "completed",
            "results": execution_results,
            "workflow_name": workflow_plan.get("workflow_name", "Unknown")
        }


class TemporalWorkflowManager:
    """Manager class for Temporal workflow operations"""
    
    def __init__(self):
        self.client = None
        self.worker = None
    
    async def initialize(self):
        """Initialize Temporal client and worker"""
        temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
        
        # Connect to Temporal server
        self.client = await Client.connect(temporal_host, namespace=temporal_namespace)
        
        # Create worker
        self.worker = Worker(
            self.client,
            task_queue="mudda-ai-workflows",
            workflows=[MuddaWorkflow],
            activities=[WorkflowActivities],
        )
    
    async def start_worker(self):
        """Start the Temporal worker"""
        if not self.worker:
            await self.initialize()
        
        await self.worker.run()
    
    async def execute_workflow(
        self, 
        workflow_plan: Dict[str, Any], 
        execution_id: str
    ) -> str:
        """
        Start execution of a workflow plan
        
        Args:
            workflow_plan: The workflow plan to execute
            execution_id: ID of the execution record
            
        Returns:
            Temporal workflow ID
        """
        if not self.client:
            await self.initialize()
        
        # Start the workflow
        handle = await self.client.start_workflow(
            MuddaWorkflow.run,
            args=[workflow_plan, execution_id],
            id=f"mudda-workflow-{execution_id}",
            task_queue="mudda-ai-workflows"
        )
        
        return handle.id
    
    async def get_workflow_result(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the result of a workflow execution
        
        Args:
            workflow_id: Temporal workflow ID
            
        Returns:
            Workflow execution result
        """
        if not self.client:
            await self.initialize()
        
        handle = self.client.get_workflow_handle(workflow_id)
        result = await handle.result()
        
        return result


# Global workflow manager instance
workflow_manager = TemporalWorkflowManager()


async def start_temporal_worker():
    """Start the Temporal worker (call this in your main application)"""
    await workflow_manager.start_worker()


async def execute_workflow_plan(
    workflow_plan: Dict[str, Any], 
    execution_id: str
) -> str:
    """
    Execute a workflow plan using Temporal
    
    Args:
        workflow_plan: The workflow plan to execute
        execution_id: ID of the execution record
        
    Returns:
        Temporal workflow ID
    """
    return await workflow_manager.execute_workflow(workflow_plan, execution_id)