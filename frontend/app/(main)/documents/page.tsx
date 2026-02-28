'use client';

import { useState, useEffect } from 'react';
import DocumentsHeader from './_components/DocumentsHeader';
import CreateDocumentModal from './_components/CreateDocumentModal';
import DocumentDetailsModal from './_components/DocumentDetailsModal';
import LoadingState from '@/components/LoadingState';
import ErrorAlert from '@/components/ErrorAlert';
import DataLayout from '@/components/DataLayout';
import { DocumentCard } from './_components/DocumentCard';
import { Document } from '@/lib/type';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalDocuments, setTotalDocuments] = useState(0);
  const pageSize = 50;

  useEffect(() => {
    fetchDocuments();
  }, [page]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/documents?page=${page}&page_size=${pageSize}`);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch documents');
      }
      const data = await response.json();
      setDocuments(data.documents);
      setTotalDocuments(data.total);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch documents');
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDocument = async (documentData: { text: string; heading: string; author: string }) => {
    try {
      setIsCreating(true);
      setCreateError(null);
      const response = await fetch('/api/documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(documentData),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create document');
      }
      const newDocument = await response.json();
      setDocuments([newDocument, ...documents]);
      setTotalDocuments(totalDocuments + 1);
      setIsCreateModalOpen(false);
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create document');
      console.error('Error creating document:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleViewDetails = (document: Document) => {
    setSelectedDocument(document);
    setIsDetailsModalOpen(true);
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to delete document');
      }
      setDocuments(documents.filter(doc => doc.id !== documentId));
      setTotalDocuments(totalDocuments - 1);
      setIsDetailsModalOpen(false);
      setSelectedDocument(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete document');
      console.error('Error deleting document:', err);
    }
  };

  return (
    <div className="p-8">
      <DocumentsHeader onCreateClick={() => setIsCreateModalOpen(true)} />

      {error && <ErrorAlert message={error} />}

      <DataLayout
        data={documents.map(d => ({ ...d, id: d.id }))}
        loading={loading}
        error={error}
        itemName="documents"
        columns={[
          {
            key: 'heading',
            header: 'Heading',
            width: 'min-w-[300px]',
            render: (document: Document) => (
              <div className="min-w-0">
                <div className="font-semibold text-gray-900 truncate">
                  {document.heading}
                </div>
              </div>
            ),
          },
          {
            key: 'author',
            header: 'Author',
            width: 'w-48',
            render: (document: Document) => (
              <span className="text-gray-700 font-medium">
                {document.author}
              </span>
            ),
          },
          {
            key: 'status',
            header: 'Status',
            width: 'w-32',
            render: (document: Document) => (
              <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                document.status === 'active'
                  ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200'
              }`}>
                {document.status}
              </span>
            ),
          },
          {
            key: 'created_at',
            header: 'Created At',
            width: 'w-40',
            render: (document: Document) => (
              <span className="text-gray-600 font-medium">
                {new Date(document.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </span>
            ),
          },
        ]}
        renderGridItem={(document: Document) => (
          <DocumentCard
            key={document.id}
            document={document}
            onClick={() => handleViewDetails(document)}
          />
        )}
        onRowClick={handleViewDetails}
        emptyMessage="No documents found. Create your first document to get started."
      />

      <CreateDocumentModal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setCreateError(null);
        }}
        onCreate={handleCreateDocument}
        isLoading={isCreating}
        error={createError}
      />

      <DocumentDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedDocument(null);
        }}
        document={selectedDocument}
        onDelete={handleDeleteDocument}
      />
    </div>
  );
}
