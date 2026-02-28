'use client';

import { FileText, User, Calendar, Trash2 } from 'lucide-react';
import { Document } from '@/lib/type';

interface DocumentCardProps {
  document: Document;
  onClick: () => void;
  onDelete: (e: React.MouseEvent) => void;
}

export function DocumentCard({ document, onClick, onDelete }: DocumentCardProps) {
  return (
    <div
      className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-all duration-200 cursor-pointer hover:border-purple-300 group relative"
    >
      {/* Delete button in top right */}
      <button
        onClick={onDelete}
        className="absolute top-4 right-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
        title="Delete document"
      >
        <Trash2 className="w-4 h-4" />
      </button>

      <div onClick={onClick}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold text-gray-900 truncate group-hover:text-purple-600 transition-colors">
                {document.heading}
              </h3>
            </div>
          </div>
          <span
            className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
              document.status === 'active'
                ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                : 'bg-gray-100 text-gray-700 border border-gray-200'
            }`}
          >
            {document.status}
          </span>
        </div>

        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{document.text}</p>

        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <User className="w-4 h-4" />
            <span>{document.author}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>
              {new Date(document.created_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
