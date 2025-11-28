'use client';

import { useState, useEffect } from 'react';
import { componentApi, Component } from '@/lib/api';
import ComponentsHeader from './components/ComponentsHeader';
import ComponentsTable from './components/ComponentsTable';
import CreateComponentModal from './components/CreateComponentModal';
import ComponentDetailsModal from './components/ComponentDetailsModal';
import LoadingState from '../workflows/components/LoadingState';
import ErrorAlert from '../workflows/components/ErrorAlert';

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
      const data = await componentApi.getAll(true);
      setComponents(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch components');
      console.error('Error fetching components:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateComponent = async (formData: any) => {
    try {
      setIsCreating(true);
      setCreateError(null);
      const newComponent = await componentApi.create(formData);
      setComponents([newComponent, ...components]);
      setIsCreateModalOpen(false);
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Failed to create component');
      console.error('Error creating component:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleViewDetails = async (component: Component) => {
    try {
      const fullComponent = await componentApi.getById(component.id);
      setSelectedComponent(fullComponent);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch component details');
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

