'use client';

import { useState, useEffect } from 'react';
import { Component } from '@/lib/type';
import ComponentsHeader from './_components/ComponentsHeader';
import ComponentsTable from './_components/ComponentsTable';
import CreateComponentModal from './_components/CreateComponentModal';
import ComponentDetailsModal from './_components/ComponentDetailsModal';
import LoadingState from '../workflows/_components/LoadingState';
import ErrorAlert from '../workflows/_components/ErrorAlert';

export default function ComponentsPage() {
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/components?active_only=true');
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch components');
      }
      const data = await response.json();
      setComponents(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch components');
      console.error('Error fetching components:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateComponent = async (formData: any) => {
    try {
      setIsCreating(true);
      setCreateError(null);
      const response = await fetch('/api/components', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create component');
      }
      const newComponent = await response.json();
      setComponents([newComponent, ...components]);
      setIsCreateModalOpen(false);
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create component');
      console.error('Error creating component:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleViewDetails = async (component: Component) => {
    try {
      const response = await fetch(`/api/components/${component.id}`);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch component details');
      }
      const fullComponent = await response.json();
      setSelectedComponent(fullComponent);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch component details');
      console.error('Error fetching component details:', err);
    }
  };

  return (
    <div className="p-8">
      <ComponentsHeader onCreateClick={() => setIsCreateModalOpen(true)} />

      {error && <ErrorAlert message={error} />}

      {loading ? (
        <LoadingState />
      ) : (
        <ComponentsTable components={components} onViewDetails={handleViewDetails} />
      )}

      <CreateComponentModal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setCreateError(null);
        }}
        onCreate={handleCreateComponent}
        isLoading={isCreating}
        error={createError}
      />

      <ComponentDetailsModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedComponent(null);
        }}
        component={selectedComponent}
      />
    </div>
  );
}

