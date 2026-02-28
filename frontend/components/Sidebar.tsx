'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, LayoutDashboard, GitBranch, Activity, FileText } from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

export default function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    document.documentElement.style.setProperty(
      '--sidebar-width',
      isCollapsed ? '80px' : '256px'
    );
  }, [isCollapsed]);

  const navigation: NavItem[] = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: <LayoutDashboard className="w-6 h-6" />,
    },
    {
      name: 'Workflows',
      href: '/workflows',
      icon: <GitBranch className="w-6 h-6" />,
    },
    {
      name: 'Activities',
      href: '/activities',
      icon: <Activity className="w-6 h-6" />,
    },
    {
      name: 'Documents',
      href: '/documents',
      icon: <FileText className="w-6 h-6" />,
    },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <div
      className={`fixed left-0 top-0 h-full transition-all duration-300 ease-in-out bg-gradient-to-b from-blue-50 via-blue-100/80 to-blue-50 shadow-xl border-r border-blue-200/50 z-50 ${isCollapsed ? 'w-20' : 'w-64'
        }`}
    >
      <div className="flex flex-col h-full relative">
        {/* Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute -right-3 top-10 w-6 h-6 bg-white border border-blue-200 rounded-full flex items-center justify-center shadow-md hover:bg-blue-50 transition-colors z-50"
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4 text-blue-600" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-blue-600" />
          )}
        </button>

        {/* Logo/Brand */}
        <div className={`flex items-center h-20 px-6 border-b border-blue-200/60 bg-white/40 backdrop-blur-sm shadow-sm transition-all duration-300 ${isCollapsed ? 'justify-center px-2' : 'justify-start'}`}>
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg transform transition-transform hover:scale-105">
              <GitBranch className="w-6 h-6 text-white" />
            </div>
            {!isCollapsed && (
              <div className="transition-opacity duration-300">
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent truncate">Mudda AI</h1>
                <p className="text-xs text-blue-600/70 font-medium">Workflow System</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-6 space-y-2 overflow-y-auto overflow-x-hidden">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                title={isCollapsed ? item.name : ''}
                className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 group relative ${active
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/40'
                  : 'text-blue-700/80 hover:bg-blue-100/60 hover:text-blue-800'
                  } ${isCollapsed ? 'justify-center' : 'space-x-4'}`}
              >
                <div className={`flex-shrink-0 transition-colors duration-200 ${active ? 'text-white' : 'text-blue-500/70 group-hover:text-blue-600'}`}>
                  {item.icon}
                </div>
                {!isCollapsed && (
                  <span className="font-semibold text-sm transition-opacity duration-300 whitespace-nowrap">
                    {item.name}
                  </span>
                )}
                {active && !isCollapsed && (
                  <div className="ml-auto w-2 h-2 bg-white rounded-full shadow-sm animate-pulse"></div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className={`px-4 py-6 border-t border-blue-200/60 bg-white/30 backdrop-blur-sm transition-all duration-300 ${isCollapsed ? 'items-center' : ''}`}>
          <div className="text-center overflow-hidden">
            <p className="text-[10px] text-blue-600/60 font-bold uppercase tracking-wider">
              {isCollapsed ? 'v0.2.6' : 'Version 0.2.6'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

