'use client';

import { Component } from '@/lib/api';
import Table from '@/components/Table';

interface ComponentsTableProps {
  components: Component[];
  onViewDetails: (component: Component) => void;
}

export default function ComponentsTable({ components, onViewDetails }: ComponentsTableProps) {
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
        onClick: onViewDetails,
      }}
      emptyMessage="No components found. Create your first component to get started."
    />
  );
}

