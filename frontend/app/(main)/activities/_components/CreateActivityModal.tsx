'use client';

import { useState } from 'react';
import Modal from '@/components/Modal';
import Button from '@/components/Button';
import { ComponentActivity, ComponentCreateRequest } from '@/lib/type';

interface CreateComponentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (formData: ComponentCreateRequest) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const initialActivity: ComponentActivity = {
  activity_name: '',
  timeout: 30,
  retry_policy: {
    maximum_attempts: 3,
    initial_interval: 1,
  },
  metadata: {}
};

export default function CreateComponentModal({
  isOpen,
  onClose,
  onCreate,
  isLoading,
  error,
}: CreateComponentModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [version, setVersion] = useState('1.0');
  const [activities, setActivities] = useState<ComponentActivity[]>([{ ...initialActivity }]);

  const handleAddActivity = () => {
    setActivities([...activities, { ...initialActivity }]);
  };

  const handleRemoveActivity = (index: number) => {
    const newActivities = activities.filter((_, i) => i !== index);
    setActivities(newActivities.length > 0 ? newActivities : [{ ...initialActivity }]);
  };

  const handleActivityChange = (index: number, field: keyof ComponentActivity, value: any) => {
    const newActivities = [...activities];
    newActivities[index] = { ...newActivities[index], [field]: value };
    setActivities(newActivities);
  };

  const handleRetryPolicyChange = (index: number, field: string, value: any) => {
    const newActivities = [...activities];
    newActivities[index] = {
      ...newActivities[index],
      retry_policy: {
        ...newActivities[index].retry_policy,
        [field]: value
      }
    };
    setActivities(newActivities);
  };

  const handleCreate = async () => {
    if (!name.trim() || activities.some(a => !a.activity_name.trim())) {
      return;
    }
    
    const request: ComponentCreateRequest = {
      name,
      description,
      category,
      version,
      activities,
      config: {}
    };

    await onCreate(request);
    if (!error) {
      handleClose();
    }
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setCategory('');
    setVersion('1.0');
    setActivities([{ ...initialActivity }]);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Create New business Component"
      size="xl"
    >
      <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2 custom-scrollbar">
        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">
              Component Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              placeholder="e.g., Emergency Response Unit"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">
              Description
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition-all resize-none"
              placeholder="What this business unit orchestrates..."
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">
              Category
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              placeholder="e.g., Infrastructure"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">
              Version
            </label>
            <input
              type="text"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
            />
          </div>
        </div>

        {/* Activities Section */}
        <div className="border-t border-gray-100 pt-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-base font-bold text-gray-900 flex items-center">
              Internal Activities
              <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded-full">
                {activities.length}
              </span>
            </h4>
            <button
              onClick={handleAddActivity}
              className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Activity
            </button>
          </div>

          <div className="space-y-4">
            {activities.map((activity, index) => (
              <div key={index} className="relative bg-gray-50 rounded-xl p-5 border border-gray-200 group">
                <button
                  onClick={() => handleRemoveActivity(index)}
                  className="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition-colors"
                  title="Remove Activity"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">
                      Activity Handler Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={activity.activity_name}
                      onChange={(e) => handleActivityChange(index, 'activity_name', e.target.value)}
                      className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 outline-none"
                      placeholder="e.g., llm_activity, send_notification"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">
                      Timeout (s)
                    </label>
                    <input
                      type="number"
                      value={activity.timeout}
                      onChange={(e) => handleActivityChange(index, 'timeout', parseInt(e.target.value))}
                      className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                  
                  <div className="md:col-span-3">
                    <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">
                      Activity Description
                    </label>
                    <input
                      type="text"
                      value={activity.description || ''}
                      onChange={(e) => handleActivityChange(index, 'description', e.target.value)}
                      className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 outline-none"
                      placeholder="Briefly describe what this activity does in this component..."
                    />
                  </div>
                  
                  {/* Retry Policy Miniature Form */}
                  <div className="md:col-span-3 grid grid-cols-2 gap-4 mt-2 bg-white p-3 rounded-lg border border-gray-100">
                    <div>
                      <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">
                        Max Retries
                      </label>
                      <input
                        type="number"
                        value={activity.retry_policy?.maximum_attempts}
                        onChange={(e) => handleRetryPolicyChange(index, 'maximum_attempts', parseInt(e.target.value))}
                        className="w-full px-2 py-1 border border-gray-100 rounded text-xs focus:ring-1 focus:ring-indigo-500 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-gray-400 uppercase mb-1">
                        Backoff (s)
                      </label>
                      <input
                        type="number"
                        value={activity.retry_policy?.initial_interval}
                        onChange={(e) => handleRetryPolicyChange(index, 'initial_interval', parseInt(e.target.value))}
                        className="w-full px-2 py-1 border border-gray-100 rounded text-xs focus:ring-1 focus:ring-indigo-500 outline-none"
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm flex items-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleCreate}
            isLoading={isLoading}
            disabled={!name.trim() || activities.some(a => !a.activity_name.trim())}
          >
            Create Component
          </Button>
        </div>
      </div>
    </Modal>
  );
}

