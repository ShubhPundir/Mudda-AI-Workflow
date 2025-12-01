'use client';

import { useState, useEffect } from 'react';
import { Workflow } from '@/lib/type';
import WorkflowsHeader from './_components/WorkflowsHeader';
import WorkflowsTable from './_components/WorkflowsTable';
import GenerateWorkflowModal from './_components/GenerateWorkflowModal';
import WorkflowDetailsModal from './_components/WorkflowDetailsModal';
import LoadingState from './_components/LoadingState';
import ErrorAlert from './_components/ErrorAlert';

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

  const handleViewDetails = async (workflow: Workflow) => {
    try {
      const response = await fetch(`/api/workflows/${workflow.workflow_id}`);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch workflow details');
      }
      const fullWorkflow = await response.json();
      setSelectedWorkflow(fullWorkflow);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch workflow details');
      console.error('Error fetching workflow details:', err);
    }
  };

  return (
    <div className="p-8">
      <WorkflowsHeader onGenerateClick={() => setIsGenerateModalOpen(true)} />

      {error && <ErrorAlert message={error} />}

      {loading ? (
        <LoadingState />
      ) : (
        <WorkflowsTable workflows={workflows} onViewDetails={handleViewDetails} />
      )}

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

