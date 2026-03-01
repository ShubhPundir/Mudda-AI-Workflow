'use client';

import { AgentStatus } from './types';

interface LoadingDotsProps {
    color: string;
}

export function LoadingDots({ color }: LoadingDotsProps) {
    const colorMap: Record<string, string> = {
        cyan: 'bg-cyan-400',
        blue: 'bg-blue-400',
        purple: 'bg-purple-400',
        green: 'bg-green-400',
    };
    
    const colorClass = colorMap[color] || 'bg-blue-400';

    return (
        <div className="flex space-x-1">
            {[0, 150, 300].map((delay) => (
                <div
                    key={delay}
                    className={`w-2 h-2 ${colorClass} rounded-full animate-bounce`}
                    style={{ animationDelay: `${delay}ms` }}
                />
            ))}
        </div>
    );
}

interface ProgressStepProps {
    stepNumber: number | string;
    label: string;
    isActive: boolean;
    isComplete: boolean;
    activeColor: string;
}

export function ProgressStep({ stepNumber, label, isActive, isComplete, activeColor }: ProgressStepProps) {
    const getStepClass = () => {
        if (isActive) {
            return `bg-${activeColor}-500 text-white scale-110 shadow-lg shadow-${activeColor}-500/50`;
        }
        if (isComplete) {
            return 'bg-green-500 text-white';
        }
        return 'bg-slate-700 text-slate-400';
    };

    return (
        <div className="flex items-center">
            <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-500 ${getStepClass()}`}
            >
                {isComplete ? '✓' : stepNumber}
            </div>
            <span className="ml-2 text-sm text-slate-300 hidden sm:inline">{label}</span>
        </div>
    );
}

interface ProgressConnectorProps {
    isComplete: boolean;
    fromColor: string;
    toColor: string;
}

export function ProgressConnector({ isComplete, fromColor, toColor }: ProgressConnectorProps) {
    return (
        <div className="w-16 h-1 bg-slate-700 rounded-full overflow-hidden">
            <div
                className={`h-full bg-gradient-to-r from-${fromColor}-500 to-${toColor}-500 transition-all duration-1000 ${isComplete ? 'w-full' : 'w-0'
                    }`}
            />
        </div>
    );
}
