'use client';

import { useState, useEffect } from 'react';
import { Workflow } from '@/lib/type';
import WorkflowsHeader from './_components/WorkflowsHeader';
import GenerateWorkflowModal from './_components/GenerateWorkflowModal';
import WorkflowDetailsModal from './_components/WorkflowDetailsModal';
import LoadingState from '@/components/LoadingState';
import ErrorAlert from '@/components/ErrorAlert';
import DataLayout from '@/components/DataLayout';
import { WorkflowCard } from './_components/WorkflowCard';

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generateError, setGenerateError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/workflows');
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch workflows');
      }
      const data = await response.json();
      setWorkflows(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch workflows');
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateWorkflow = async (problemStatement: string) => {
    try {
      setIsGenerating(true);
      setGenerateError(null);
      const response = await fetch('/api/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ problem_statement: problemStatement }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to generate workflow');
      }
      const newWorkflow = await response.json();
      setWorkflows([newWorkflow, ...workflows]);
      setIsGenerateModalOpen(false);
    } catch (err: any) {
      setGenerateError(err.message || 'Failed to generate workflow');
      console.error('Error generating workflow:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleViewDetails = (workflow: Workflow) => {
    window.location.href = `/workflows/${workflow.workflow_id}`;
  };

  return (
    <div className="p-8">
      <WorkflowsHeader onGenerateClick={() => setIsGenerateModalOpen(true)} />

      {error && <ErrorAlert message={error} />}

      <DataLayout
        data={workflows.map(w => ({ ...w, id: w.workflow_id }))}
        loading={loading}
        error={error}
        itemName="workflows"
        columns={[
          {
            key: 'workflow_plan',
            header: 'Workflow Name',
            width: 'min-w-[300px]',
            render: (workflow: Workflow) => (
              <div className="min-w-0">
                <div className="font-semibold text-gray-900 truncate">
                  {workflow?.workflow_plan?.workflow_name || 'Unnamed Workflow'}
                </div>
              </div>
            ),
          },
          {
            key: 'status',
            header: 'Status',
            width: 'w-32',
            render: (workflow: Workflow) => (
              <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${workflow.status === 'active' || workflow.status === 'ACTIVE'
                ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                : workflow.status === 'DRAFT'
                  ? 'bg-amber-100 text-amber-700 border border-amber-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200'
                }`}>
                {workflow.status}
              </span>
            ),
          },
          {
            key: 'created_at',
            header: 'Created At',
            width: 'w-40',
            render: (workflow: Workflow) => (
              <span className="text-gray-600 font-medium">
                {new Date(workflow.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </span>
            ),
          },
          {
            key: 'steps',
            header: 'Steps',
            width: 'w-24',
            render: (workflow: Workflow) => (
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span className="text-gray-700 font-medium">
                  {workflow?.workflow_plan?.steps?.length || 0}
                </span>
              </div>
            ),
          },
        ]}
        renderGridItem={(workflow: Workflow) => (
          <WorkflowCard
            key={workflow.workflow_id}
            workflow={workflow}
            onClick={() => handleViewDetails(workflow)}
          />
        )}
        onRowClick={handleViewDetails}
        emptyMessage="No workflows found. Generate your first workflow to get started."
      />

      <GenerateWorkflowModal
        isOpen={isGenerateModalOpen}
        onClose={() => {
          setIsGenerateModalOpen(false);
          setGenerateError(null);
        }}
        onGenerate={handleGenerateWorkflow}
        isLoading={isGenerating}
        error={generateError}
      />

      <WorkflowDetailsModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedWorkflow(null);
        }}
        workflow={selectedWorkflow}
      />
    </div>
  );
}

