import React from 'react';
import { ComponentActivity } from '@/lib/type';

interface ActivityCardProps {
    component: ComponentActivity;
    onClick: () => void;
}

export default function ActivityCard({ component, onClick }: ActivityCardProps) {
    return (
        <div
            onClick={onClick}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group"
        >
            <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                </div>
                <span className={`px-2 py-1 text-[10px] uppercase font-bold rounded-md bg-emerald-50 text-emerald-600`}>
                    Active
                </span>
            </div>

            <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors truncate">
                {(component as any).id || component.activity_name}
            </h3>

            <p className="text-gray-500 text-sm line-clamp-2 mb-4 h-10">
                {component.description || 'No description provided'}
            </p>

            <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                <div className="flex items-center space-x-1.5">
                    <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                        {Object.keys((component as any).inputs || {}).length}
                    </span>
                    <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
                        Inputs
                    </span>
                </div>
                <div className="flex items-center text-primary-600 text-xs font-bold group-hover:translate-x-1 transition-transform">
                    View Details
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        </div>
    );
}
