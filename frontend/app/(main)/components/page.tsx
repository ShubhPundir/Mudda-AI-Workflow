'use client';

import { useState, useEffect } from 'react';
import { componentApi, Component } from '@/lib/api';
import Table from '@/components/Table';
import Modal from '@/components/Modal';
import Button from '@/components/Button';

export default function ComponentsPage() {
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'REST',
    category: '',
    endpoint_url: '',
    http_method: 'GET',
    auth_type: 'NONE',
    version: '1.0',
  });

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

  const handleCreateComponent = async () => {
    if (!formData.name.trim() || !formData.endpoint_url.trim()) {
      setError('Name and endpoint URL are required');
      return;
    }

    try {
      setIsCreating(true);
      setError(null);
      const newComponent = await componentApi.create(formData);
      setComponents([newComponent, ...components]);
      setFormData({
        name: '',
        description: '',
        type: 'REST',
        category: '',
        endpoint_url: '',
        http_method: 'GET',
        auth_type: 'NONE',
        version: '1.0',
      });
      setIsCreateModalOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create component');
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

  const columns = [
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
      key: 'type',
      header: 'Type',
      width: 'w-28',
      render: (component: Component) => (
        <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-700 border border-blue-200">
          {component.type}
        </span>
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
      key: 'endpoint_url',
      header: 'Endpoint',
      width: 'min-w-[300px]',
      render: (component: Component) => (
        <div className="flex items-center space-x-2 min-w-0">
          <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <span className="text-sm text-gray-600 font-mono truncate">
            {component.endpoint_url}
          </span>
        </div>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      width: 'w-28',
      render: (component: Component) => (
        <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${
          component.is_active 
            ? 'bg-emerald-100 text-emerald-700 border-emerald-200' 
            : 'bg-gray-100 text-gray-700 border-gray-200'
        }`}>
          {component.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Components</h1>
          <p className="text-gray-500">
            Manage API components for workflow integration
          </p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          variant="primary"
          size="lg"
          className="flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Component</span>
        </Button>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-center space-x-2 shadow-sm">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="text-center py-16">
          <div className="inline-block relative">
            <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-6 h-6 bg-primary-100 rounded-full"></div>
            </div>
          </div>
          <p className="mt-4 text-gray-600 font-medium">Loading components...</p>
        </div>
      ) : (
        <Table
          data={components}
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
          emptyMessage="No components found. Create your first component to get started."
        />
      )}

      {/* Create Component Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setFormData({
            name: '',
            description: '',
            type: 'REST',
            category: '',
            endpoint_url: '',
            http_method: 'GET',
            auth_type: 'NONE',
            version: '1.0',
          });
          setError(null);
        }}
        title="Create New Component"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-2.5">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              placeholder="Component name"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2.5">
              Description
            </label>
            <textarea
              id="description"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all resize-none"
              placeholder="What the API/component does"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="type" className="block text-sm font-semibold text-gray-700 mb-2.5">
                Type <span className="text-red-500">*</span>
              </label>
              <select
                id="type"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white"
              >
                <option value="REST">REST</option>
                <option value="RPC">RPC</option>
                <option value="GraphQL">GraphQL</option>
              </select>
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-semibold text-gray-700 mb-2.5">
                Category
              </label>
              <input
                type="text"
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                placeholder="e.g., Issue Management"
              />
            </div>
          </div>

          <div>
            <label htmlFor="endpoint_url" className="block text-sm font-semibold text-gray-700 mb-2.5">
              Endpoint URL <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="endpoint_url"
              value={formData.endpoint_url}
              onChange={(e) => setFormData({ ...formData, endpoint_url: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-mono text-sm transition-all"
              placeholder="https://api.example.com/endpoint/{id}"
            />
          </div>

          {formData.type === 'REST' && (
            <div>
              <label htmlFor="http_method" className="block text-sm font-semibold text-gray-700 mb-2.5">
                HTTP Method
              </label>
              <select
                id="http_method"
                value={formData.http_method}
                onChange={(e) => setFormData({ ...formData, http_method: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white"
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="PATCH">PATCH</option>
                <option value="DELETE">DELETE</option>
              </select>
            </div>
          )}

          <div>
            <label htmlFor="auth_type" className="block text-sm font-semibold text-gray-700 mb-2.5">
              Authentication Type
            </label>
            <select
              id="auth_type"
              value={formData.auth_type}
              onChange={(e) => setFormData({ ...formData, auth_type: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white"
            >
              <option value="NONE">None</option>
              <option value="API_KEY">API Key</option>
              <option value="BEARER">Bearer Token</option>
              <option value="BASIC">Basic Auth</option>
              <option value="OAUTH2">OAuth2</option>
            </select>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm flex items-center space-x-2">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-2">
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateModalOpen(false);
                setFormData({
                  name: '',
                  description: '',
                  type: 'REST',
                  category: '',
                  endpoint_url: '',
                  http_method: 'GET',
                  auth_type: 'NONE',
                  version: '1.0',
                });
                setError(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateComponent}
              isLoading={isCreating}
            >
              Create
            </Button>
          </div>
        </div>
      </Modal>

      {/* Component Details Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedComponent(null);
        }}
        title={selectedComponent?.name || 'Component Details'}
        size="xl"
      >
        {selectedComponent && (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
              <p className="text-gray-900">{selectedComponent.description || 'N/A'}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Type</h4>
                <span className="inline-flex px-2 py-1 text-sm font-semibold rounded-full bg-blue-100 text-blue-800">
                  {selectedComponent.type}
                </span>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Category</h4>
                <p className="text-gray-900">{selectedComponent.category || 'N/A'}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Status</h4>
                <span className={`inline-flex px-2 py-1 text-sm font-semibold rounded-full ${
                  selectedComponent.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {selectedComponent.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Version</h4>
                <p className="text-gray-900">{selectedComponent.version || '1.0'}</p>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">Endpoint URL</h4>
              <p className="text-gray-900 font-mono text-sm bg-gray-50 p-2 rounded">
                {selectedComponent.endpoint_url}
              </p>
            </div>

            {selectedComponent.http_method && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">HTTP Method</h4>
                <p className="text-gray-900">{selectedComponent.http_method}</p>
              </div>
            )}

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">Authentication</h4>
              <p className="text-gray-900">{selectedComponent.auth_type || 'NONE'}</p>
            </div>

            {selectedComponent.created_at && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Created At</h4>
                <p className="text-gray-900">
                  {new Date(selectedComponent.created_at).toLocaleString()}
                </p>
              </div>
            )}

            {Object.keys(selectedComponent.request_schema || {}).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-2">Request Schema</h4>
                <pre className="text-xs bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto">
                  {JSON.stringify(selectedComponent.request_schema, null, 2)}
                </pre>
              </div>
            )}

            {Object.keys(selectedComponent.response_schema || {}).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-2">Response Schema</h4>
                <pre className="text-xs bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto">
                  {JSON.stringify(selectedComponent.response_schema, null, 2)}
                </pre>
              </div>
            )}

            {selectedComponent.owner_service && (
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">Owner Service</h4>
                <p className="text-gray-900">{selectedComponent.owner_service}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

