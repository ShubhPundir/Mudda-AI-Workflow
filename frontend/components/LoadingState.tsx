import React from 'react';

interface LoadingStateProps {
    message?: string;
}

export default function LoadingState({ message = 'Loading data...' }: LoadingStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-20 px-4">
            <div className="relative w-16 h-16">
                <div className="absolute inset-0 border-4 border-primary-100 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <p className="mt-6 text-gray-500 font-medium animate-pulse">{message}</p>
        </div>
    );
}
