'use client';

import { useState, useEffect } from 'react';
import { workflowApi, Workflow } from '@/lib/api';
import Table from '@/components/Table';
import Modal from '@/components/Modal';
import Button from '@/components/Button';

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [problemStatement, setProblemStatement] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await workflowApi.getAll();
      setWorkflows(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch workflows');
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateWorkflow = async () => {
    if (!problemStatement.trim()) {
      setError('Please enter a problem statement');
      return;
    }

    try {
      setIsGenerating(true);
      setError(null);
      const newWorkflow = await workflowApi.generate({
        problem_statement: problemStatement,
      });
      setWorkflows([newWorkflow, ...workflows]);
      setProblemStatement('');
      setIsGenerateModalOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate workflow');
      console.error('Error generating workflow:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleViewDetails = async (workflow: Workflow) => {
    try {
      const fullWorkflow = await workflowApi.getById(workflow.workflow_id);
      setSelectedWorkflow(fullWorkflow);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch workflow details');
      console.error('Error fetching workflow details:', err);
    }
  };

  const columns = [
    {
      key: 'workflow_plan',
      header: 'Workflow Name',
      render: (workflow: Workflow) => (
        <div>
          <div className="font-medium text-gray-900">
            {workflow?.workflow_plan?.workflow_name || 'Unnamed Workflow'}
          </div>
          <div className="text-gray-500 text-xs mt-1">
            {workflow?.workflow_plan?.description || 'No description'}
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (workflow: Workflow) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          workflow.status === 'active' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {workflow.status}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Created At',
      render: (workflow: Workflow) => (
        <span>{new Date(workflow.created_at).toLocaleDateString()}</span>
      ),
    },
    {
      key: 'steps',
      header: 'Steps',
      render: (workflow: Workflow) => (
        <span className="text-gray-600">
          {workflow?.workflow_plan?.steps?.length || 0} steps
        </span>
      ),
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage and generate AI-powered workflows for civic issues
          </p>
        </div>
        <Button
          onClick={() => setIsGenerateModalOpen(true)}
          variant="primary"
          size="lg"
        >
          Generate Workflow
        </Button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-gray-600">Loading workflows...</p>
        </div>
      ) : (
        <Table
          data={workflows}
          columns={columns}
          actionButton={{
            label: 'Info',
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ),
            onClick: handleViewDetails,
          }}
          emptyMessage="No workflows found. Generate your first workflow to get started."
        />
      )}

      {/* Generate Workflow Modal */}
      <Modal
        isOpen={isGenerateModalOpen}
        onClose={() => {
          setIsGenerateModalOpen(false);
          setProblemStatement('');
          setError(null);
        }}
        title="Generate New Workflow"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="problem-statement" className="block text-sm font-medium text-gray-700 mb-2">
              Problem Statement
            </label>
            <textarea
              id="problem-statement"
              rows={6}
              value={problemStatement}
              onChange={(e) => setProblemStatement(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Describe the civic issue you want to resolve (e.g., 'Resolve pothole issue reported in Ward 22')"
            />
          </div>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => {
                setIsGenerateModalOpen(false);
                setProblemStatement('');
                setError(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleGenerateWorkflow}
              isLoading={isGenerating}
            >
              Generate
            </Button>
          </div>
        </div>
      </Modal>

      {/* Workflow Details Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedWorkflow(null);
        }}
        title={selectedWorkflow?.workflow_plan.workflow_name || 'Workflow Details'}
        size="xl"
      >
        {selectedWorkflow && (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
              <p className="text-gray-900">{selectedWorkflow.workflow_plan?.description || 'No description'}</p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Status</h4>
              <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
                selectedWorkflow.status === 'active' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {selectedWorkflow.status}
              </span>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Created At</h4>
              <p className="text-gray-900">
                {new Date(selectedWorkflow.created_at).toLocaleString()}
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-3">Workflow Steps</h4>
              <div className="space-y-4">
                {selectedWorkflow.workflow_plan?.steps?.length > 0 ? (
                  selectedWorkflow.workflow_plan.steps.map((step, index) => (
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
        )}
      </Modal>
    </div>
  );
}

