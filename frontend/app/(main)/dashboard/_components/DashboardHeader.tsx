'use client';

interface DashboardHeaderProps {
  selectedPeriod: 'week' | 'month' | 'year';
  onPeriodChange: (period: 'week' | 'month' | 'year') => void;
}

export default function DashboardHeader({ selectedPeriod, onPeriodChange }: DashboardHeaderProps) {
  return (
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
              onClick={() => onPeriodChange(period)}
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
  );
}

