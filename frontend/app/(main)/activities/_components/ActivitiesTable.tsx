'use client';

import { ComponentActivity } from '@/lib/type';
import Table from '@/components/Table';

interface ActivitiesTableProps {
  components: ComponentActivity[];
  onViewDetails: (component: ComponentActivity) => void;
}

export default function ActivitiesTable({ components, onViewDetails }: ActivitiesTableProps) {
  const columns = [
    {
      key: 'activity_name',
      header: 'Activity Name',
      width: 'min-w-[280px]',
      render: (activity: ComponentActivity) => (
        <div className="min-w-0">
          <div className="font-semibold text-gray-900 truncate">{(activity as any).id || activity.activity_name}</div>
          {activity.description && (
            <div className="text-gray-500 text-xs mt-1 line-clamp-2">{activity.description}</div>
          )}
        </div>
      ),
    },
    {
      key: 'inputs',
      header: 'Inputs',
      width: 'w-28',
      render: (activity: ComponentActivity) => (
        <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-700 border border-blue-200">
          {Object.keys((activity as any).inputs || {}).length} Inputs
        </span>
      ),
    },
    {
      key: 'outputs',
      header: 'Outputs',
      width: 'w-40',
      render: (activity: ComponentActivity) => (
        <span className="text-gray-600 font-medium">
          {Object.keys((activity as any).outputs || {}).length} Outputs
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      width: 'w-28',
      render: (activity: ComponentActivity) => (
        <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border bg-emerald-100 text-emerald-700 border-emerald-200`}>
          Active
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
      emptyMessage="No activities found."
    />
  );
}

