'use client';

import { Component } from '@/lib/api';
import Modal from '@/components/Modal';

interface ComponentDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  component: Component | null;
}

export default function ComponentDetailsModal({
  isOpen,
  onClose,
  component,
}: ComponentDetailsModalProps) {
  if (!component) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={component.name || 'Component Details'}
      size="xl"
    >
      <div className="space-y-6">
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
          <p className="text-gray-900">{component.description || 'N/A'}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Type</h4>
            <span className="inline-flex px-2 py-1 text-sm font-semibold rounded-full bg-blue-100 text-blue-800">
              {component.type}
            </span>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Category</h4>
            <p className="text-gray-900">{component.category || 'N/A'}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Status</h4>
            <span className={`inline-flex px-2 py-1 text-sm font-semibold rounded-full ${
              component.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {component.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Version</h4>
            <p className="text-gray-900">{component.version || '1.0'}</p>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-1">Endpoint URL</h4>
          <p className="text-gray-900 font-mono text-sm bg-gray-50 p-2 rounded">
            {component.endpoint_url}
          </p>
        </div>

        {component.http_method && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">HTTP Method</h4>
            <p className="text-gray-900">{component.http_method}</p>
          </div>
        )}

        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-1">Authentication</h4>
          <p className="text-gray-900">{component.auth_type || 'NONE'}</p>
        </div>

        {component.created_at && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Created At</h4>
            <p className="text-gray-900">
              {new Date(component.created_at).toLocaleString()}
            </p>
          </div>
        )}

        {Object.keys(component.request_schema || {}).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Request Schema</h4>
            <pre className="text-xs bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto">
              {JSON.stringify(component.request_schema, null, 2)}
            </pre>
          </div>
        )}

        {Object.keys(component.response_schema || {}).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Response Schema</h4>
            <pre className="text-xs bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto">
              {JSON.stringify(component.response_schema, null, 2)}
            </pre>
          </div>
        )}

        {component.owner_service && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Owner Service</h4>
            <p className="text-gray-900">{component.owner_service}</p>
          </div>
        )}
      </div>
    </Modal>
  );
}

