'use client';

import { Component } from '@/lib/type';
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
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Owner Service</h4>
            <p className="text-gray-900">{component.owner_service || 'N/A'}</p>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-6">
          <h4 className="text-base font-bold text-gray-900 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Activities ({component.activities?.length || 0})
          </h4>
          
          <div className="space-y-4">
            {component.activities && component.activities.length > 0 ? (
              component.activities.map((activity, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-600 text-white text-[10px] font-bold">
                        {index + 1}
                      </span>
                      <h5 className="font-bold text-gray-900">{activity.activity_name}</h5>
                    </div>
                    {activity.timeout && (
                      <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-tighter">
                        Timeout: {activity.timeout}s
                      </span>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                    {activity.retry_policy && (
                      <div className="bg-white p-3 rounded-lg border border-gray-100">
                        <p className="text-[10px] font-bold text-gray-400 uppercase mb-2">Retry Policy</p>
                        <div className="grid grid-cols-2 gap-1 text-xs">
                          <span className="text-gray-500">Max Attempts:</span>
                          <span className="text-gray-900 font-medium">{activity.retry_policy.maximum_attempts || 'Default'}</span>
                          <span className="text-gray-500">Initial Interval:</span>
                          <span className="text-gray-900 font-medium">{activity.retry_policy.initial_interval ? `${activity.retry_policy.initial_interval}s` : 'Default'}</span>
                        </div>
                      </div>
                    )}
                    
                    {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                      <div className="bg-white p-3 rounded-lg border border-gray-100">
                        <p className="text-[10px] font-bold text-gray-400 uppercase mb-2">Metadata</p>
                        <div className="space-y-1">
                          {Object.entries(activity.metadata).map(([key, value]) => (
                            <div key={key} className="flex justify-between text-xs">
                              <span className="text-gray-500">{key}:</span>
                              <span className="text-gray-900 font-medium truncate ml-2" title={String(value)}>
                                {String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 italic">No activities defined for this component.</p>
            )}
          </div>
        </div>

        {component.config && Object.keys(component.config).length > 0 && (
          <div className="border-t border-gray-100 pt-6">
            <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center">
              <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Global Configuration
            </h4>
            <pre className="text-xs bg-gray-50 p-4 rounded-xl border border-gray-100 overflow-x-auto text-gray-600">
              {JSON.stringify(component.config, null, 2)}
            </pre>
          </div>
        )}

        {component.created_at && (
          <div className="text-[10px] text-gray-400 text-right pt-4">
            ID: {component.id} • Registered on {new Date(component.created_at).toLocaleDateString()}
          </div>
        )}
      </div>
    </Modal>
  );
}

