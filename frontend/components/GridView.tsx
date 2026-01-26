import React from 'react';

interface GridViewProps<T> {
    data: T[];
    renderItem: (item: T) => React.ReactNode;
    emptyMessage?: string;
    gridClassName?: string;
}

function GridView<T extends { id?: string | number }>({
    data,
    renderItem,
    emptyMessage = 'No items found',
    gridClassName = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6',
}: GridViewProps<T>) {
    if (data.length === 0) {
        return (
            <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
                <div className="flex flex-col items-center justify-center">
                    <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-gray-500 text-base font-medium">{emptyMessage}</p>
                </div>
            </div>
        );
    }

    return (
        <div className={gridClassName}>
            {data.map((item, index) => (
                <React.Fragment key={item.id || index}>
                    {renderItem(item)}
                </React.Fragment>
            ))}
        </div>
    );
}

export default GridView;
