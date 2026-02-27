'use client';

import { useState, useEffect } from 'react';
import { Component } from '@/lib/type';
import ComponentsHeader from './_components/ComponentsHeader';
import ComponentsTable from './_components/ComponentsTable';
import CreateComponentModal from './_components/CreateComponentModal';
import ComponentDetailsModal from './_components/ComponentDetailsModal';
import LoadingState from '@/components/LoadingState';
import ErrorAlert from '@/components/ErrorAlert';
import DataLayout from '@/components/DataLayout';
import ComponentCard from './_components/ComponentCard';

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

      <DataLayout
        data={components}
        loading={loading}
        error={error}
        itemName="components"
        columns={[
          {
            key: 'name',
            header: 'Component Name',
            width: 'min-w-[280px]',
            render: (component: Component) => (
              <div className="min-w-0">
                <div className="font-semibold text-gray-900 truncate">{component.name}</div>
                {component.description && (
                  <div className="text-gray-500 text-xs mt-1 line-clamp-2">{component.description}</div>
                )}
              </div>
            ),
          },
          {
            key: 'activities',
            header: 'Activities',
            width: 'w-48',
            render: (component: Component) => (
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-200">
                  {component.activities?.length || 0} Activities
                </span>
                <div className="flex -space-x-1 overflow-hidden">
                  {component.activities?.slice(0, 3).map((act, idx) => (
                    <div 
                      key={idx}
                      className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-100 flex items-center justify-center text-[8px] font-bold text-gray-500 border border-gray-200"
                      title={act.activity_name}
                    >
                      {act.activity_name.substring(0, 2).toUpperCase()}
                    </div>
                  ))}
                  {(component.activities?.length || 0) > 3 && (
                    <div className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-50 flex items-center justify-center text-[8px] font-bold text-gray-400 border border-gray-200">
                      +{(component.activities?.length || 0) - 3}
                    </div>
                  )}
                </div>
              </div>
            ),
          },
          {
            key: 'category',
            header: 'Category',
            width: 'w-40',
            render: (component: Component) => (
              <span className="text-gray-600 font-medium">{component.category || 'N/A'}</span>
            ),
          },
          {
            key: 'is_active',
            header: 'Status',
            width: 'w-28',
            render: (component: Component) => (
              <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${component.is_active
                ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
                : 'bg-gray-100 text-gray-700 border-gray-200'
                }`}>
                {component.is_active ? 'Active' : 'Inactive'}
              </span>
            ),
          },
        ]}
        renderGridItem={(component) => (
          <ComponentCard
            key={component.id}
            component={component}
            onClick={() => handleViewDetails(component)}
          />
        )}
        onRowClick={handleViewDetails}
        emptyMessage="No components found. Create your first component to get started."
      />

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

