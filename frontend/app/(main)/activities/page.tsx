'use client';

import { useState, useEffect } from 'react';
import { ComponentActivity } from '@/lib/type';
import ActivitiesHeader from './_components/ActivitiesHeader';
import ActivitiesTable from './_components/ActivitiesTable';
import CreateActivityModal from './_components/CreateActivityModal';
import ActivityDetailsModal from './_components/ActivityDetailsModal';
import LoadingState from '@/components/LoadingState';
import ErrorAlert from '@/components/ErrorAlert';
import DataLayout from '@/components/DataLayout';
import ActivityCard from './_components/ActivityCard';

export default function ActivitiesPage() {
  const [activities, setActivities] = useState<ComponentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedActivity, setSelectedActivity] = useState<ComponentActivity | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    fetchActivities();
  }, []);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/activities');
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch activities');
      }
      const data = await response.json();
      setActivities(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch activities');
      console.error('Error fetching activities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateActivity = async (formData: any) => {
    try {
      setIsCreating(true);
      setCreateError(null);
      const response = await fetch('/api/activities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create activity');
      }
      const newActivity = await response.json();
      setActivities([newActivity, ...activities]);
      setIsCreateModalOpen(false);
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create activity');
      console.error('Error creating activity:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleViewDetails = async (activity: ComponentActivity) => {
    try {
      // NOTE: Activities from registry might not have a detailed endpoint, so we can mock or use what's returned.
      setSelectedActivity(activity);
      setIsModalOpen(true);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch activity details');
      console.error('Error fetching activity details:', err);
    }
  };

  return (
    <div className="p-8">
      <ActivitiesHeader onCreateClick={() => setIsCreateModalOpen(true)} />

      {error && <ErrorAlert message={error} />}

      <DataLayout
        data={activities}
        loading={loading}
        error={error}
        itemName="activities"
        columns={[
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
            width: 'w-48',
            render: (activity: ComponentActivity) => (
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-200">
                  {Object.keys((activity as any).inputs || {}).length} Inputs
                </span>
                <div className="flex -space-x-1 overflow-hidden">
                  {((activity as any).inputs || []).slice(0, 3).map((inp: string, idx: number) => (
                    <div 
                      key={idx}
                      className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-100 flex items-center justify-center text-[8px] font-bold text-gray-500 border border-gray-200"
                      title={inp}
                    >
                      {inp.substring(0, 2).toUpperCase()}
                    </div>
                  ))}
                  {(((activity as any).inputs || []).length || 0) > 3 && (
                    <div className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-50 flex items-center justify-center text-[8px] font-bold text-gray-400 border border-gray-200">
                      +{(((activity as any).inputs || []).length || 0) - 3}
                    </div>
                  )}
                </div>
              </div>
            ),
          },
          {
            key: 'outputs',
            header: 'Outputs',
            width: 'w-40',
            render: (activity: ComponentActivity) => (
              <span className="text-gray-600 font-medium">{Object.keys((activity as any).outputs || {}).length} Outputs</span>
            ),
          },
          {
            key: 'status',
            header: 'Status',
            width: 'w-28',
            render: (activity: ComponentActivity) => (
              <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border bg-emerald-100 text-emerald-700 border-emerald-200`}>
                Active
              </span>
            ),
          },
        ]}
        renderGridItem={(activity) => (
          <ActivityCard
            key={(activity as any).id}
            component={activity as any}
            onClick={() => handleViewDetails(activity as any)}
          />
        )}
        onRowClick={(activity) => handleViewDetails(activity as any)}
        emptyMessage="No activities found."
      />

      <CreateActivityModal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setCreateError(null);
        }}
        onCreate={handleCreateActivity}
        isLoading={isCreating}
        error={createError}
      />

      <ActivityDetailsModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedActivity(null);
        }}
        component={selectedActivity}
      />
    </div>
  );
}

