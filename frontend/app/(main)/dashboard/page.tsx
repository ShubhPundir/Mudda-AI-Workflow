'use client';

import { useState } from 'react';
import DashboardHeader from './_components/DashboardHeader';
import StatsGrid from './_components/StatsGrid';
import GeographicMapSection from './_components/GeographicMapSection';
import RecentActivity from './_components/RecentActivity';
import ResolutionTrend from './_components/ResolutionTrend';
import IssueCategories from './_components/IssueCategories';

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

const recentActivities = [
  { type: 'resolved' as const, title: 'Pothole Repair', location: 'Vasant Vihar', time: '2h ago' },
  { type: 'active' as const, title: 'Street Light Fix', location: 'Saket Metro Station', time: '4h ago' },
  { type: 'pending' as const, title: 'Garbage Collection', location: 'Vasant Kunj', time: '6h ago' },
  { type: 'resolved' as const, title: 'Water Leak', location: 'Iffco Chowk', time: '8h ago' },
  { type: 'active' as const, title: 'Sidewalk Repair', location: 'Kalkaji Mandir', time: '10h ago' },
];

const issueCategories = [
  { category: 'Infrastructure', count: 456, percentage: 36.5, gradient: 'bg-gradient-to-r from-blue-500 to-blue-600' },
  { category: 'Public Safety', count: 312, percentage: 25.0, gradient: 'bg-gradient-to-r from-rose-500 to-pink-500' },
  { category: 'Environmental', count: 287, percentage: 23.0, gradient: 'bg-gradient-to-r from-emerald-500 to-teal-500' },
  { category: 'Utilities', count: 192, percentage: 15.5, gradient: 'bg-gradient-to-r from-amber-500 to-orange-500' },
];

export default function DashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');

  return (
    <div className="p-8">
      <DashboardHeader selectedPeriod={selectedPeriod} onPeriodChange={setSelectedPeriod} />

      <StatsGrid analytics={staticAnalytics} />

      {/* Map and Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <GeographicMapSection issues={sampleIssues} />
        <RecentActivity activities={recentActivities} />
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ResolutionTrend resolutionRate={staticAnalytics.resolutionRate} period={selectedPeriod} />
        <IssueCategories categories={issueCategories} />
      </div>
    </div>
  );
}

