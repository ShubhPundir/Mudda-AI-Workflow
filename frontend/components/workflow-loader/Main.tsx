'use client';

import { useEffect, useState } from 'react';
import { LoaderState, AGENTS } from './types';
import { AgentCard } from './AgentCard';
import { ProgressTimeline } from './ProgressTimeline';
import { ComponentGrid } from './ComponentGrid';
import { ErrorDisplay } from './ErrorDisplay';
import { loaderStyles } from './styles';

interface WorkflowGenerationLoaderProps {
    isActive: boolean;
}

const INITIAL_STATE: LoaderState = {
    agent1Status: 'idle',
    agent2Status: 'idle',
    selectedComponents: [],
    currentMessage: 'Initializing AI agents...',
    stage: 'component_selection',
};

export default function WorkflowGenerationLoader({ isActive }: WorkflowGenerationLoaderProps) {
    const [state, setState] = useState<LoaderState>(INITIAL_STATE);

    useEffect(() => {
        if (isActive) {
            setState({
                ...INITIAL_STATE,
                agent1Status: 'active',
                currentMessage: 'Agent 1: Analyzing problem and selecting components...',
            });
        }
    }, [isActive]);

    const updateState = (updates: Partial<LoaderState>) => {
        setState((prev) => ({ ...prev, ...updates }));
    };

    // Expose update function for parent component
    useEffect(() => {
        (window as any).__updateLoaderState = updateState;
        return () => {
            delete (window as any).__updateLoaderState;
        };
    }, []);

    if (!isActive) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="w-full max-w-5xl mx-4 p-8 bg-gradient-to-br from-slate-900/95 to-slate-800/95 rounded-2xl shadow-2xl border border-slate-700/50 backdrop-blur-xl">
                {/* Header */}
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        AI Workflow Generation
                    </h2>
                    <p className="text-slate-300 text-sm">{state.currentMessage}</p>
                </div>

                {/* Progress Timeline */}
                <ProgressTimeline state={state} />

                {/* Agent Cards */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <AgentCard agent={AGENTS[0]} status={state.agent1Status} state={state} />
                    <AgentCard agent={AGENTS[1]} status={state.agent2Status} state={state} />
                </div>

                {/* Selected Components */}
                <ComponentGrid components={state.selectedComponents} />

                {/* Error State */}
                {state.stage === 'error' && <ErrorDisplay message={state.currentMessage} />}
            </div>

            <style jsx>{loaderStyles}</style>
        </div>
    );
}
