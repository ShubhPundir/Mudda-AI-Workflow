'use client';

import { Workflow } from '@/lib/api';
import Table from '@/components/Table';

interface WorkflowsTableProps {
  workflows: Workflow[];
  onViewDetails: (workflow: Workflow) => void;
}

export default function WorkflowsTable({ workflows, onViewDetails }: WorkflowsTableProps) {
  const columns = [
    {
      key: 'workflow_plan',
      header: 'Workflow Name',
      width: 'min-w-[300px]',
      render: (workflow: Workflow) => (
        <div className="min-w-0">
          <div className="font-semibold text-gray-900 truncate">
            {workflow?.workflow_plan?.workflow_name || 'Unnamed Workflow'}
          </div>
          <div className="text-gray-500 text-xs mt-1 line-clamp-2">
            {workflow?.workflow_plan?.description || 'No description'}
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      width: 'w-32',
      render: (workflow: Workflow) => (
        <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
          workflow.status === 'active' || workflow.status === 'ACTIVE'
            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
            : workflow.status === 'DRAFT'
            ? 'bg-amber-100 text-amber-700 border border-amber-200'
            : 'bg-gray-100 text-gray-700 border border-gray-200'
        }`}>
          {workflow.status}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Created At',
      width: 'w-40',
      render: (workflow: Workflow) => (
        <span className="text-gray-600 font-medium">
          {new Date(workflow.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          })}
        </span>
      ),
    },
    {
      key: 'steps',
      header: 'Steps',
      width: 'w-24',
      render: (workflow: Workflow) => (
        <div className="flex items-center space-x-1">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span className="text-gray-700 font-medium">
            {workflow?.workflow_plan?.steps?.length || 0}
          </span>
        </div>
      ),
    },
  ];

  return (
    <Table
      data={workflows}
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
      emptyMessage="No workflows found. Generate your first workflow to get started."
    />
  );
}

