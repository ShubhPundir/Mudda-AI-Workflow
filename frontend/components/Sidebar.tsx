'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

export default function Sidebar() {
  const pathname = usePathname();

  const navigation: NavItem[] = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
    },
    {
      name: 'Workflows',
      href: '/workflows',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      ),
    },
    {
      name: 'Components',
      href: '/components',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
    },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-gradient-to-b from-blue-50 via-blue-100/80 to-blue-50 shadow-xl border-r border-blue-200/50 z-50">
      <div className="flex flex-col h-full">
        {/* Logo/Brand */}
        <div className="flex items-center justify-center h-20 px-6 border-b border-blue-200/60 bg-white/40 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Mudda AI</h1>
              <p className="text-xs text-blue-600/70 font-medium">Workflow System</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-4 px-4 py-3 rounded-xl transition-all duration-200 group ${active
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/40'
                  : 'text-blue-700/80 hover:bg-blue-100/60 hover:text-blue-800'
                  }`}
              >
                <div className={`flex-shrink-0 ${active ? 'text-white' : 'text-blue-500/70 group-hover:text-blue-600'}`}>
                  {item.icon}
                </div>
                <span className="font-semibold text-sm">{item.name}</span>
                {active && (
                  <div className="ml-auto w-2 h-2 bg-white rounded-full shadow-sm"></div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-4 py-6 border-t border-blue-200/60 bg-white/30 backdrop-blur-sm">
          <div className="text-center">
            <p className="text-xs text-blue-600/60 font-medium">Version 0.2.6</p>
          </div>
        </div>
      </div>
    </div>
  );
}

