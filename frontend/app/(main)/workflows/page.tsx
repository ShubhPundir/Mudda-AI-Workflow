'use client';

import { useState, useEffect } from 'react';
import { workflowApi, Workflow } from '@/lib/api';
import WorkflowsHeader from './components/WorkflowsHeader';
import WorkflowsTable from './components/WorkflowsTable';
import GenerateWorkflowModal from './components/GenerateWorkflowModal';
import WorkflowDetailsModal from './components/WorkflowDetailsModal';
import LoadingState from './components/LoadingState';
import ErrorAlert from './components/ErrorAlert';

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

  const handleGenerateWorkflow = async (problemStatement: string) => {
    try {
      setIsGenerating(true);
      setGenerateError(null);
      const newWorkflow = await workflowApi.generate({
        problem_statement: problemStatement,
      });
      setWorkflows([newWorkflow, ...workflows]);
      setIsGenerateModalOpen(false);
    } catch (err: any) {
      setGenerateError(err.response?.data?.detail || 'Failed to generate workflow');
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

