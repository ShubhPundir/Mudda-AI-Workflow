import StatCard from './StatCard';

interface AnalyticsData {
  totalIssues: number;
  resolvedIssues: number;
  activeIssues: number;
  avgResolutionTime: string;
  resolutionRate: number;
}

interface StatsGridProps {
  analytics: AnalyticsData;
}

export default function StatsGrid({ analytics }: StatsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        title="Total Issues"
        value={analytics.totalIssues.toLocaleString()}
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
        value={analytics.resolvedIssues.toLocaleString()}
        subtitle={`${analytics.resolutionRate}% resolution rate`}
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
        value={analytics.activeIssues.toLocaleString()}
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
        value={analytics.avgResolutionTime}
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
  );
}

