'use client';

import { Component } from './types';

interface ComponentGridProps {
    components: Component[];
}

export function ComponentGrid({ components }: ComponentGridProps) {
    if (components.length === 0) return null;

    return (
        <div className="mb-6">
            <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                Selected Components ({components.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto custom-scrollbar">
                {components.map((component, index) => (
                    <ComponentCard key={component.id} component={component} index={index} />
                ))}
            </div>
        </div>
    );
}

interface ComponentCardProps {
    component: Component;
    index: number;
}

function ComponentCard({ component, index }: ComponentCardProps) {
    return (
        <div
            className="p-3 bg-slate-800/70 border border-slate-700/50 rounded-lg hover:border-blue-500/50 transition-all duration-300 animate-fade-in"
            style={{ animationDelay: `${index * 50}ms` }}
        >
            <h5 className="text-sm font-semibold text-white mb-1">{component.name}</h5>
            <p className="text-xs text-slate-400 line-clamp-2">{component.description}</p>
        </div>
    );
}
