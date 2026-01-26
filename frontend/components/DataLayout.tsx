import React, { useState } from 'react';
import Table from './Table';
import GridView from './GridView';
import ViewToggle, { ViewMode } from './ViewToggle';
import LoadingState from './LoadingState';
import ErrorAlert from './ErrorAlert';

interface DataLayoutProps<T> {
    data: T[];
    columns: any[];
    renderGridItem: (item: T) => React.ReactNode;
    loading?: boolean;
    error?: string | null;
    onRowClick?: (item: T) => void;
    actionButton?: {
        label: string;
        icon?: React.ReactNode;
        onClick: (item: T) => void;
    };
    emptyMessage?: string;
    gridClassName?: string;
    itemName?: string;
}

function DataLayout<T extends { id?: any;[key: string]: any }>({
    data,
    columns,
    renderGridItem,
    loading = false,
    error = null,
    onRowClick,
    actionButton,
    emptyMessage,
    gridClassName,
    itemName = 'items',
}: DataLayoutProps<T>) {
    const [viewMode, setViewMode] = useState<ViewMode>('table');

    if (loading) {
        return <LoadingState message={`Loading ${itemName}...`} />;
    }

    if (error) {
        return <ErrorAlert message={error} />;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-end">
                <ViewToggle mode={viewMode} onModeChange={setViewMode} />
            </div>

            {viewMode === 'table' ? (
                <Table
                    data={data}
                    columns={columns}
                    onRowClick={onRowClick}
                    actionButton={actionButton}
                    emptyMessage={emptyMessage}
                />
            ) : (
                <GridView
                    data={data}
                    renderItem={renderGridItem}
                    emptyMessage={emptyMessage}
                    gridClassName={gridClassName}
                />
            )}
        </div>
    );
}

export default DataLayout;
