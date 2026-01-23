import React from 'react';

export type ViewMode = 'table' | 'grid';

interface ViewToggleProps {
    mode: ViewMode;
    onModeChange: (mode: ViewMode) => void;
}

export default function ViewToggle({ mode, onModeChange }: ViewToggleProps) {
    return (
        <div className="flex items-center bg-gray-100 p-1 rounded-lg">
            <button
                onClick={() => onModeChange('table')}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${mode === 'table'
                        ? 'bg-white text-primary-600 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
            >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                <span>Table</span>
            </button>
            <button
                onClick={() => onModeChange('grid')}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${mode === 'grid'
                        ? 'bg-white text-primary-600 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
            >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4h7v7H4V4zM13 4h7v7h-7V4zM4 13h7v7H4v-7zM13 13h7v7h-7v-7z" />
                </svg>
                <span>Grid</span>
            </button>
        </div>
    );
}
