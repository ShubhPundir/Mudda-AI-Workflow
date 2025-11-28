'use client';

import { useState } from 'react';
import GeographicMap from '@/components/GeographicMap';

// Static data for demonstration
const staticAnalytics = {
  totalIssues: 1247,
  resolvedIssues: 892,
  activeIssues: 287,
  pendingIssues: 68,
  resolutionRate: 71.5,
  avgResolutionTime: '3.2 days',
};

// Sample issues from India
const sampleIssues = [
  // Delhi NCR
  { id: '1', lat: 28.6139, lng: 77.2090, status: 'active' as const, title: 'Pothole Repair - New Delhi' },
  { id: '2', lat: 28.5355, lng: 77.3910, status: 'resolved' as const, title: 'Street Light Fix - Gurgaon' },
  { id: '3', lat: 28.4089, lng: 77.3178, status: 'active' as const, title: 'Garbage Collection - Noida' },
  { id: '4', lat: 28.6692, lng: 77.4538, status: 'pending' as const, title: 'Water Leak - Ghaziabad' },
  { id: '5', lat: 28.4089, lng: 77.0926, status: 'resolved' as const, title: 'Traffic Signal - Faridabad' },
  // Mumbai
  { id: '6', lat: 19.0760, lng: 72.8777, status: 'active' as const, title: 'Sidewalk Repair - Mumbai' },
  { id: '7', lat: 19.2183, lng: 72.9781, status: 'resolved' as const, title: 'Park Maintenance - Navi Mumbai' },
  // Bangalore
  { id: '8', lat: 12.9716, lng: 77.5946, status: 'active' as const, title: 'Drainage Issue - Bangalore' },
  // Chennai
  { id: '9', lat: 13.0827, lng: 80.2707, status: 'pending' as const, title: 'Tree Removal - Chennai' },
  // Kolkata
  { id: '10', lat: 22.5726, lng: 88.3639, status: 'resolved' as const, title: 'Road Maintenance - Kolkata' },
  // Hyderabad
  { id: '11', lat: 17.3850, lng: 78.4867, status: 'active' as const, title: 'Street Cleaning - Hyderabad' },
  // Pune
  { id: '12', lat: 18.5204, lng: 73.8567, status: 'resolved' as const, title: 'Bridge Repair - Pune' },
];

const StatCard = ({ title, value, subtitle, icon, color, gradient }: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
  gradient: string;
}) => {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-lg hover:border-blue-200 transition-all">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl ${gradient} shadow-md`}>
          {icon}
        </div>
        <span className="text-xs font-semibold text-blue-600/70 uppercase tracking-wide">{title}</span>
      </div>
      <div className="space-y-1">
        <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{value}</h3>
        {subtitle && <p className="text-sm text-blue-600/60 font-medium">{subtitle}</p>}
      </div>
    </div>
  );
};

export default function DashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Dashboard</h1>
            <p className="text-blue-600/70 font-medium mt-1">Overview of workflow analytics and active issues</p>
          </div>
          <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-lg border border-blue-200/50 p-1 shadow-sm">
            {(['week', 'month', 'year'] as const).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-md text-sm font-semibold transition-all ${
                  selectedPeriod === period
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-md'
                    : 'text-blue-600/70 hover:text-blue-700 hover:bg-blue-50/50'
                }`}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Issues"
          value={staticAnalytics.totalIssues.toLocaleString()}
          subtitle="All time"
          color="bg-blue-100 text-blue-600"
          gradient="bg-gradient-to-br from-blue-400 to-blue-500 text-white"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        />
        <StatCard
          title="Resolved"
          value={staticAnalytics.resolvedIssues.toLocaleString()}
          subtitle={`${staticAnalytics.resolutionRate}% resolution rate`}
          color="bg-emerald-100 text-emerald-600"
          gradient="bg-gradient-to-br from-emerald-400 to-teal-500 text-white"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          title="Active Issues"
          value={staticAnalytics.activeIssues.toLocaleString()}
          subtitle="Currently in progress"
          color="bg-rose-100 text-rose-600"
          gradient="bg-gradient-to-br from-rose-400 to-pink-500 text-white"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          title="Avg Resolution"
          value={staticAnalytics.avgResolutionTime}
          subtitle="Time to resolve"
          color="bg-amber-100 text-amber-600"
          gradient="bg-gradient-to-br from-amber-400 to-orange-500 text-white"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
        />
      </div>

      {/* Map and Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Geographic Map */}
        <div className="lg:col-span-2">
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Geographic Distribution</h2>
                <p className="text-sm text-blue-600/60 font-medium mt-1">Active issues across regions</p>
              </div>
              <div className="flex items-center space-x-2 text-sm text-blue-600/70 font-medium">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-rose-500 shadow-sm"></div>
                  <span>Active</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm"></div>
                  <span>Resolved</span>
                </div>
              </div>
            </div>
            <GeographicMap issues={sampleIssues} height="500px" />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { type: 'resolved', title: 'Pothole Repair', location: 'Manhattan', time: '2h ago' },
              { type: 'active', title: 'Street Light Fix', location: 'Brooklyn', time: '4h ago' },
              { type: 'pending', title: 'Garbage Collection', location: 'Queens', time: '6h ago' },
              { type: 'resolved', title: 'Water Leak', location: 'Bronx', time: '8h ago' },
              { type: 'active', title: 'Sidewalk Repair', location: 'Staten Island', time: '10h ago' },
            ].map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  activity.type === 'resolved' ? 'bg-green-500' :
                  activity.type === 'active' ? 'bg-red-500' : 'bg-amber-500'
                }`}></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{activity.title}</p>
                  <p className="text-xs text-gray-500">{activity.location}</p>
                  <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resolution Trend */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">Resolution Trend</h2>
          <div className="h-64 flex items-center justify-center">
            <div className="text-center">
              <div className="w-32 h-32 mx-auto mb-4 relative">
                <svg className="transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="url(#progressGradient)"
                    strokeWidth="8"
                    strokeDasharray={`${staticAnalytics.resolutionRate * 2.51} 251`}
                    strokeLinecap="round"
                  />
                  <defs>
                    <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#6366f1" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{staticAnalytics.resolutionRate}%</span>
                </div>
              </div>
              <p className="text-sm text-blue-600/70 font-medium">Issues resolved this {selectedPeriod}</p>
            </div>
          </div>
        </div>

        {/* Issue Categories */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">Issue Categories</h2>
          <div className="space-y-4">
              {[
              { category: 'Infrastructure', count: 456, percentage: 36.5, gradient: 'bg-gradient-to-r from-blue-500 to-blue-600' },
              { category: 'Public Safety', count: 312, percentage: 25.0, gradient: 'bg-gradient-to-r from-rose-500 to-pink-500' },
              { category: 'Environmental', count: 287, percentage: 23.0, gradient: 'bg-gradient-to-r from-emerald-500 to-teal-500' },
              { category: 'Utilities', count: 192, percentage: 15.5, gradient: 'bg-gradient-to-r from-amber-500 to-orange-500' },
            ].map((item, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-blue-700">{item.category}</span>
                  <span className="text-sm font-bold text-blue-600">{item.count}</span>
                </div>
                <div className="w-full bg-blue-100/50 rounded-full h-3 shadow-inner">
                  <div
                    className={`${item.gradient} h-3 rounded-full transition-all duration-500 shadow-sm`}
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                <span className="text-xs text-blue-600/70 font-medium mt-1">{item.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

