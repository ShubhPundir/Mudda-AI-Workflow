'use client';

import { ComponentActivity } from '@/lib/type';
import Modal from '@/components/Modal';

interface ActivityDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  component: ComponentActivity | null;
}

export default function ActivityDetailsModal({
  isOpen,
  onClose,
  component,
}: ActivityDetailsModalProps) {
  if (!component) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={(component as any).id || component.activity_name || 'Activity Details'}
      size="lg"
    >
      <div className="space-y-6">
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
          <p className="text-gray-900">{component.description || 'N/A'}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Internal Name</h4>
            <p className="text-gray-900 font-mono text-sm bg-gray-50 px-2 py-1 rounded inline-block">{component.activity_name}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Status</h4>
            <span className={`inline-flex px-2 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-800`}>
              Active
            </span>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">Timeout</h4>
            <p className="text-gray-900">{component.timeout ? `${component.timeout}s` : 'System Default'}</p>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-6">
          <h4 className="text-base font-bold text-gray-900 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            I/O Signatures
          </h4>
          
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h5 className="font-bold text-gray-900 mb-2">Inputs</h5>
                <div className="flex flex-wrap gap-2">
                    {((component as any).inputs || []).length > 0 ? (
                        ((component as any).inputs || []).map((input: string, idx: number) => (
                            <span key={idx} className="bg-indigo-50 text-indigo-700 text-xs font-mono px-2 py-1 rounded border border-indigo-100">
                                {input}
                            </span>
                        ))
                    ) : (
                        <span className="text-xs text-gray-500 italic">No required inputs</span>
                    )}
                </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h5 className="font-bold text-gray-900 mb-2">Outputs</h5>
                <div className="flex flex-wrap gap-2">
                    {((component as any).outputs || []).length > 0 ? (
                        ((component as any).outputs || []).map((output: string, idx: number) => (
                            <span key={idx} className="bg-emerald-50 text-emerald-700 text-xs font-mono px-2 py-1 rounded border border-emerald-100">
                                {output}
                            </span>
                        ))
                    ) : (
                        <span className="text-xs text-gray-500 italic">No specific outputs</span>
                    )}
                </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
}

