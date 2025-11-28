import React from 'react';

interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => React.ReactNode;
  width?: string; // e.g., "w-64", "w-1/4", "min-w-[200px]"
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  actionButton?: {
    label: string;
    icon?: React.ReactNode;
    onClick: (item: T) => void;
  };
  emptyMessage?: string;
}

function Table<T extends { id?: string; [key: string]: any }>({
  data,
  columns,
  onRowClick,
  actionButton,
  emptyMessage = 'No data available',
}: TableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="flex flex-col items-center justify-center">
          <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p className="text-gray-500 text-base font-medium">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gradient-to-r from-gray-50 to-gray-100/50">
            <tr>
              {columns.map((column, index) => (
                <th
                  key={index}
                  className={`px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider ${
                    column.width || ''
                  }`}
                  style={column.width ? {} : { width: 'auto' }}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.header}</span>
                  </div>
                </th>
              ))}
              {actionButton && (
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider w-32">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {data.map((item, rowIndex) => (
              <tr
                key={item.id || rowIndex}
                onClick={() => onRowClick?.(item)}
                className={`transition-all duration-150 ${
                  onRowClick ? 'cursor-pointer hover:bg-primary-50/30' : 'hover:bg-gray-50/50'
                }`}
              >
                {columns.map((column, colIndex) => (
                  <td 
                    key={colIndex} 
                    className={`px-6 py-4 text-sm text-gray-900 ${
                      column.width || ''
                    }`}
                  >
                    <div className="truncate">
                      {column.render
                        ? column.render(item)
                        : (item[column.key as keyof T] as React.ReactNode)}
                    </div>
                  </td>
                ))}
                {actionButton && (
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        actionButton.onClick(item);
                      }}
                      className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg text-primary-700 bg-primary-50 hover:bg-primary-100 border border-primary-200/50 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1"
                    >
                      {actionButton.icon && <span className="mr-1.5">{actionButton.icon}</span>}
                      {actionButton.label}
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Table;

