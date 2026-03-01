'use client';

import { Policy } from './types';

interface PolicyGridProps {
    policies: Policy[];
}

export function PolicyGrid({ policies }: PolicyGridProps) {
    if (policies.length === 0) return null;

    return (
        <div className="mb-6">
            <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
                <span className="w-2 h-2 bg-cyan-400 rounded-full mr-2 animate-pulse" />
                Retrieved Policies ({policies.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto custom-scrollbar">
                {policies.map((policy, index) => (
                    <PolicyCard key={index} policy={policy} index={index} />
                ))}
            </div>
        </div>
    );
}

interface PolicyCardProps {
    policy: Policy;
    index: number;
}

function PolicyCard({ policy, index }: PolicyCardProps) {
    const relevancePercentage = Math.round(policy.similarity_score * 100);
    
    return (
        <div
            className="p-3 bg-slate-800/70 border border-slate-700/50 rounded-lg hover:border-cyan-500/50 transition-all duration-300 animate-fade-in"
            style={{ animationDelay: `${index * 50}ms` }}
        >
            <div className="flex items-start justify-between mb-1">
                <h5 className="text-sm font-semibold text-white flex-1 line-clamp-1">{policy.heading}</h5>
                <span className="text-xs font-medium text-cyan-400 ml-2 whitespace-nowrap">
                    {relevancePercentage}%
                </span>
            </div>
            <p className="text-xs text-slate-400">by {policy.author}</p>
        </div>
    );
}
