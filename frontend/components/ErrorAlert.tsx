import React from 'react';

interface ErrorAlertProps {
    message: string;
}

export default function ErrorAlert({ message }: ErrorAlertProps) {
    return (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg shadow-sm my-4">
            <div className="flex items-center">
                <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div className="ml-3">
                    <p className="text-sm text-red-700 font-medium">
                        {message}
                    </p>
                </div>
            </div>
        </div>
    );
}
