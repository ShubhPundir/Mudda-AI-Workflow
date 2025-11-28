interface ResolutionTrendProps {
  resolutionRate: number;
  period: string;
}

export default function ResolutionTrend({ resolutionRate, period }: ResolutionTrendProps) {
  return (
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
                strokeDasharray={`${resolutionRate * 2.51} 251`}
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
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{resolutionRate}%</span>
            </div>
          </div>
          <p className="text-sm text-blue-600/70 font-medium">Issues resolved this {period}</p>
        </div>
      </div>
    </div>
  );
}

