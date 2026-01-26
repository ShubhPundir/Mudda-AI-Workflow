import React from 'react';
import { Workflow } from '@/lib/type';

interface WorkflowCardProps {
    workflow: Workflow;
    onClick: () => void;
}

export function WorkflowCard({ workflow, onClick }: WorkflowCardProps) {
    const statusColors = {
        ACTIVE: 'bg-emerald-50 text-emerald-600',
        active: 'bg-emerald-50 text-emerald-600',
        DRAFT: 'bg-amber-50 text-amber-600',
        INACTIVE: 'bg-gray-50 text-gray-500',
    };

    const status = workflow.status as keyof typeof statusColors;

    return (
        <div
            onClick={onClick}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group flex flex-col h-full"
        >
            <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-purple-50 rounded-lg group-hover:bg-purple-100 transition-colors">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                </div>
                <span className={`px-2 py-1 text-[10px] uppercase font-bold rounded-md ${statusColors[status] || 'bg-gray-50 text-gray-500'}`}>
                    {workflow.status}
                </span>
            </div>

            <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors line-clamp-2 min-h-[3.5rem]">
                {workflow?.workflow_plan?.workflow_name || 'Unnamed Workflow'}
            </h3>

            <div className="flex items-center text-gray-500 text-xs mt-auto pt-4 border-t border-gray-50">
                <div className="flex items-center mr-4">
                    <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {new Date(workflow.created_at).toLocaleDateString()}
                </div>
                <div className="flex items-center">
                    <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    {workflow?.workflow_plan?.steps?.length || 0} Steps
                </div>
            </div>

            <div className="mt-4 flex items-center text-primary-600 text-xs font-bold group-hover:translate-x-1 transition-transform">
                View Details
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
            </div>
        </div>
    );
}
