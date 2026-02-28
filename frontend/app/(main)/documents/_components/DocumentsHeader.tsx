'use client';

import { FileText, Plus } from 'lucide-react';

interface DocumentsHeaderProps {
  onCreateClick: () => void;
}

export default function DocumentsHeader({ onCreateClick }: DocumentsHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
            <p className="text-gray-600 mt-1">Manage your document library</p>
          </div>
        </div>
        <button
          onClick={onCreateClick}
          className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-xl hover:from-purple-600 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <Plus className="w-5 h-5" />
          <span className="font-semibold">Create Document</span>
        </button>
      </div>
    </div>
  );
}
