'use client';

import { useState } from 'react';
import Modal from '@/components/Modal';
import Button from '@/components/Button';

interface ComponentFormData {
  name: string;
  description: string;
  type: string;
  category: string;
  endpoint_url: string;
  http_method: string;
  auth_type: string;
  version: string;
}

interface CreateComponentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (formData: ComponentFormData) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const initialFormData: ComponentFormData = {
  name: '',
  description: '',
  type: 'REST',
  category: '',
  endpoint_url: '',
  http_method: 'GET',
  auth_type: 'NONE',
  version: '1.0',
};

export default function CreateComponentModal({
  isOpen,
  onClose,
  onCreate,
  isLoading,
  error,
}: CreateComponentModalProps) {
  const [formData, setFormData] = useState<ComponentFormData>(initialFormData);

  const handleCreate = async () => {
    if (!formData.name.trim() || !formData.endpoint_url.trim()) {
      return;
    }
    await onCreate(formData);
    if (!error) {
      setFormData(initialFormData);
    }
  };

  const handleClose = () => {
    setFormData(initialFormData);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Create New Component"
      size="lg"
    >
      <div className="space-y-5">
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
            onClick={handleClose}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleCreate}
            isLoading={isLoading}
            disabled={!formData.name.trim() || !formData.endpoint_url.trim()}
          >
            Create
          </Button>
        </div>
      </div>
    </Modal>
  );
}

