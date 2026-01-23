'use client';

interface ErrorDisplayProps {
    message: string;
}

export function ErrorDisplay({ message }: ErrorDisplayProps) {
    return (
        <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
            <div className="flex items-center space-x-2 text-red-400">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
                <span className="font-semibold">Error occurred during generation</span>
            </div>
            <p className="text-sm text-red-300 mt-2">{message}</p>
        </div>
    );
}
