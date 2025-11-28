'use client';

import { Workflow } from '@/lib/type';
import Modal from '@/components/Modal';
import WorkflowGraph from './WorkflowGraph';

interface WorkflowDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  workflow: Workflow | null;
}

export default function WorkflowDetailsModal({
  isOpen,
  onClose,
  workflow,
}: WorkflowDetailsModalProps) {
  if (!workflow) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={workflow.workflow_plan?.workflow_name || 'Workflow Details'}
      size="xl"
    >
      <div className="space-y-6">
        {/* Workflow Graph */}
        {workflow.workflow_plan?.steps && workflow.workflow_plan.steps.length > 0 && (
          <WorkflowGraph steps={workflow.workflow_plan.steps} />
        )}

        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
          <p className="text-gray-900">{workflow.workflow_plan?.description || 'No description'}</p>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2">Status</h4>
          <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
            workflow.status === 'active' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {workflow.status}
          </span>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2">Created At</h4>
          <p className="text-gray-900">
            {new Date(workflow.created_at).toLocaleString()}
          </p>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-4">Workflow Steps</h4>
          {workflow.workflow_plan?.steps?.length > 0 ? (
            <div className="relative">
              {/* Vertical Timeline Line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-blue-500 to-blue-400"></div>
              
              <div className="space-y-6">
                {workflow.workflow_plan.steps.map((step, index) => {
                  const isLast = index === workflow.workflow_plan.steps.length - 1;
                  return (
                    <div key={step.step_id} className="relative flex items-start">
                      {/* Timeline Node */}
                      <div className="relative z-10 flex-shrink-0">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg border-4 border-white">
                          <span className="text-white font-bold text-sm">{index + 1}</span>
                        </div>
                        {!isLast && (
                          <div className="absolute left-1/2 top-12 w-0.5 h-6 bg-gradient-to-b from-blue-400 to-blue-500 transform -translate-x-1/2"></div>
                        )}
                      </div>

                      {/* Step Content */}
                      <div className="ml-6 flex-1 pb-6">
                        <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <h5 className="font-bold text-gray-900 text-lg mb-1">
                                {step.step_id}
                              </h5>
                              <p className="text-sm text-gray-600">{step.description}</p>
                            </div>
                            {step.requires_approval && (
                              <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-200 ml-3">
                                Requires Approval
                              </span>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-100">
                            <div>
                              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Component ID</span>
                              <p className="text-sm text-gray-900 font-medium mt-1">{step.component_id}</p>
                            </div>
                            <div>
                              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Next Steps</span>
                              <p className="text-sm text-gray-900 font-medium mt-1">
                                {step.next.length > 0 ? (
                                  <span className="flex flex-wrap gap-1">
                                    {step.next.map((next, idx) => (
                                      <span key={idx} className="inline-flex px-2 py-0.5 text-xs font-medium rounded bg-indigo-100 text-indigo-700">
                                        {next}
                                      </span>
                                    ))}
                                  </span>
                                ) : (
                                  <span className="text-gray-400">None</span>
                                )}
                              </p>
                            </div>
                          </div>

                          {Object.keys(step.inputs).length > 0 && (
                            <div className="mt-4 pt-4 border-t border-gray-100">
                              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">Inputs</span>
                              <pre className="mt-2 text-xs bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto font-mono">
                                {JSON.stringify(step.inputs, null, 2)}
                              </pre>
                            </div>
                          )}

                          {step.outputs.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-gray-100">
                              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">Outputs</span>
                              <div className="mt-2 flex flex-wrap gap-2">
                                {step.outputs.map((output, idx) => (
                                  <span
                                    key={idx}
                                    className="inline-flex px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 border border-blue-200"
                                  >
                                    {output}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No steps defined for this workflow.</p>
          )}
        </div>
      </div>
    </Modal>
  );
}

