'use client';

import { useState } from 'react';
import Modal from '@/components/Modal';
import { X, FileText } from 'lucide-react';

interface CreateDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (documentData: { text: string; heading: string; author: string }) => void;
  isLoading: boolean;
  error: string | null;
}

export default function CreateDocumentModal({
  isOpen,
  onClose,
  onCreate,
  isLoading,
  error,
}: CreateDocumentModalProps) {
  const [heading, setHeading] = useState('');
  const [author, setAuthor] = useState('');
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreate({ text, heading, author });
  };

  const handleClose = () => {
    if (!isLoading) {
      setHeading('');
      setAuthor('');
      setText('');
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose}>
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">Create New Document</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={isLoading}
            className="text-white/80 hover:text-white transition-colors disabled:opacity-50"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="heading" className="block text-sm font-semibold text-gray-700 mb-2">
                Heading <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="heading"
                value={heading}
                onChange={(e) => setHeading(e.target.value)}
                required
                maxLength={255}
                placeholder="Enter document heading"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                disabled={isLoading}
              />
            </div>

            <div>
              <label htmlFor="author" className="block text-sm font-semibold text-gray-700 mb-2">
                Author <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="author"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                required
                maxLength={255}
                placeholder="Enter author name"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                disabled={isLoading}
              />
            </div>

            <div>
              <label htmlFor="text" className="block text-sm font-semibold text-gray-700 mb-2">
                Content <span className="text-red-500">*</span>
              </label>
              <textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                required
                rows={8}
                placeholder="Enter document content"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
                disabled={isLoading}
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={isLoading}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !heading.trim() || !author.trim() || !text.trim()}
                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg hover:from-purple-600 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg"
              >
                {isLoading ? 'Creating...' : 'Create Document'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Modal>
  );
}
