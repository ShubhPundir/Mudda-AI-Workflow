'use client';

import { AgentStatus, AgentConfig, LoaderState } from './types';
import { LoadingDots } from './Primitives';

interface AgentCardProps {
    agent: AgentConfig;
    status: AgentStatus;
    state: LoaderState;
}

export function AgentCard({ agent, status, state }: AgentCardProps) {
    const { activeColor } = agent;

    const getCardClass = () => {
        if (status === 'active') {
            return `bg-gradient-to-br from-${activeColor}-500/20 to-${activeColor}-600/10 border-${activeColor}-500/50 shadow-lg shadow-${activeColor}-500/20`;
        }
        if (status === 'complete') {
            return 'bg-gradient-to-br from-green-500/20 to-green-600/10 border-green-500/50';
        }
        return 'bg-slate-800/50 border-slate-700/50';
    };

    const getIconClass = () => {
        if (status === 'active') {
            return `bg-${activeColor}-500 shadow-lg shadow-${activeColor}-500/50 animate-bounce`;
        }
        if (status === 'complete') {
            return 'bg-green-500';
        }
        return 'bg-slate-700';
    };

    const getMessage = () => {
        if (status === 'active') return agent.activeMessage;
        if (status === 'complete') {
            return typeof agent.completeMessage === 'function'
                ? agent.completeMessage(state)
                : agent.completeMessage;
        }
        return agent.idleMessage;
    };

    return (
        <div className={`relative p-6 rounded-xl border transition-all duration-500 ${getCardClass()}`}>
            {/* Animated pulse effect */}
            {status === 'active' && (
                <div className={`absolute inset-0 rounded-xl bg-${activeColor}-500/10 animate-pulse`} />
            )}

            <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl transition-all duration-500 ${getIconClass()}`}>
                            {agent.icon}
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white">{agent.name}</h3>
                            <p className="text-xs text-slate-400">{agent.role}</p>
                        </div>
                    </div>

                    {status === 'complete' && (
                        <div className="text-green-400 text-2xl">✓</div>
                    )}
                    {status === 'active' && (
                        <LoadingDots color={activeColor} />
                    )}
                </div>

                <p className="text-sm text-slate-300">{getMessage()}</p>
            </div>
        </div>
    );
}
