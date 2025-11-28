'use client';

import { Workflow } from '@/lib/api';
import Modal from '@/components/Modal';

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
          <h4 className="text-sm font-medium text-gray-500 mb-3">Workflow Steps</h4>
          <div className="space-y-4">
            {workflow.workflow_plan?.steps?.length > 0 ? (
              workflow.workflow_plan.steps.map((step, index) => (
                <div
                  key={step.step_id}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h5 className="font-semibold text-gray-900">
                        Step {index + 1}: {step.step_id}
                      </h5>
                      <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                    </div>
                    {step.requires_approval && (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        Requires Approval
                      </span>
                    )}
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Component ID:</span>
                      <span className="ml-2 text-gray-600">{step.component_id}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Next Steps:</span>
                      <span className="ml-2 text-gray-600">
                        {step.next.length > 0 ? step.next.join(', ') : 'None'}
                      </span>
                    </div>
                  </div>
                  {Object.keys(step.inputs).length > 0 && (
                    <div className="mt-3">
                      <span className="font-medium text-gray-700 text-sm">Inputs:</span>
                      <pre className="mt-1 text-xs bg-white p-2 rounded border border-gray-200 overflow-x-auto">
                        {JSON.stringify(step.inputs, null, 2)}
                      </pre>
                    </div>
                  )}
                  {step.outputs.length > 0 && (
                    <div className="mt-2">
                      <span className="font-medium text-gray-700 text-sm">Outputs:</span>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {step.outputs.map((output, idx) => (
                          <span
                            key={idx}
                            className="inline-flex px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800"
                          >
                            {output}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No steps defined for this workflow.</p>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
}

