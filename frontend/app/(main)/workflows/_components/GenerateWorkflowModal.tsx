'use client';

import { useState } from 'react';
import Modal from '@/components/Modal';
import Button from '@/components/Button';
import WorkflowGenerationLoader from '@/components/WorkflowGenerationLoader';

interface GenerateWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (problemStatement: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

interface Component {
  id: string;
  name: string;
  description: string;
}

export default function GenerateWorkflowModal({
  isOpen,
  onClose,
  onGenerate,
  isLoading,
  error,
}: GenerateWorkflowModalProps) {
  const [problemStatement, setProblemStatement] = useState('');
  const [showLoader, setShowLoader] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  const updateLoaderState = (updates: any) => {
    if (typeof window !== 'undefined' && (window as any).__updateLoaderState) {
      (window as any).__updateLoaderState(updates);
    }
  };

  const handleGenerateWithStream = async () => {
    if (!problemStatement.trim()) {
      return;
    }

    setShowLoader(true);
    setStreamError(null);

    try {
      const response = await fetch('/api/workflows/generate/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ problem_statement: problemStatement }),
      });

      if (!response.ok) {
        throw new Error('Failed to start workflow generation');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let currentEvent = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.substring(6).trim();
          } else if (line.startsWith('data:')) {
            const dataStr = line.substring(5).trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              // Handle different event types
              if (currentEvent === 'component_selection_start') {
                updateLoaderState({
                  agent1Status: 'active',
                  agent2Status: 'idle',
                  currentMessage: data.message,
                  stage: 'component_selection',
                });
              } else if (currentEvent === 'component_selection_complete') {
                updateLoaderState({
                  agent1Status: 'complete',
                  selectedComponents: data.components || [],
                  currentMessage: data.message,
                });
              } else if (currentEvent === 'workflow_generation_start') {
                updateLoaderState({
                  agent2Status: 'active',
                  currentMessage: data.message,
                  stage: 'workflow_generation',
                });
              } else if (currentEvent === 'workflow_generation_complete') {
                updateLoaderState({
                  agent2Status: 'complete',
                  currentMessage: data.message,
                });
              } else if (currentEvent === 'workflow_saved') {
                updateLoaderState({
                  stage: 'complete',
                  currentMessage: 'Workflow saved successfully!',
                });
              } else if (currentEvent === 'done') {
                // Wait a bit to show success state, then close
                setTimeout(() => {
                  setShowLoader(false);
                  setProblemStatement('');
                  onClose();
                  // Trigger a refresh of the workflows list
                  window.location.reload();
                }, 2000);
              } else if (currentEvent === 'error') {
                setStreamError(data.message);
                updateLoaderState({
                  stage: 'error',
                  currentMessage: data.message,
                });
                setShowLoader(false);
              }
            } catch (parseError) {
              console.error('Failed to parse SSE data:', parseError);
            }
          }
        }
      }

    } catch (err: any) {
      setStreamError(err.message || 'Failed to start workflow generation');
      updateLoaderState({
        stage: 'error',
        currentMessage: err.message || 'Failed to start workflow generation',
      });
      setShowLoader(false);
    }
  };

  const handleClose = () => {
    setShowLoader(false);
    setProblemStatement('');
    setStreamError(null);
    onClose();
  };

  return (
    <>
      <WorkflowGenerationLoader isActive={showLoader} />

      <Modal
        isOpen={isOpen && !showLoader}
        onClose={handleClose}
        title="Generate New Workflow"
        size="lg"
      >
        <div className="space-y-5">
          <div>
            <label htmlFor="problem-statement" className="block text-sm font-semibold text-gray-700 mb-2.5">
              Problem Statement
            </label>
            <textarea
              id="problem-statement"
              rows={6}
              value={problemStatement}
              onChange={(e) => setProblemStatement(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all resize-none"
              placeholder="Describe the civic issue you want to resolve (e.g., 'Resolve pothole issue reported in Ward 22')"
            />
          </div>
          {(error || streamError) && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm flex items-center space-x-2">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error || streamError}</span>
            </div>
          )}
          <div className="flex justify-end space-x-3 pt-2">
            <Button
              variant="outline"
              onClick={handleClose}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleGenerateWithStream}
              isLoading={isLoading}
              disabled={!problemStatement.trim()}
            >
              Generate
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
