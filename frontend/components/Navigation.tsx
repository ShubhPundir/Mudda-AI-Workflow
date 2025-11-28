'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200/60 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center shadow-sm">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent">
                  Mudda AI Workflow
                </h1>
              </div>
            </div>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
              <Link
                href="/workflows"
                className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/workflows')
                    ? 'bg-primary-50 text-primary-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <svg className={`w-4 h-4 mr-2 ${isActive('/workflows') ? 'text-primary-600' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                Workflows
              </Link>
              <Link
                href="/components"
                className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/components')
                    ? 'bg-primary-50 text-primary-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <svg className={`w-4 h-4 mr-2 ${isActive('/components') ? 'text-primary-600' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Components
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

