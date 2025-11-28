interface Activity {
  type: 'resolved' | 'active' | 'pending';
  title: string;
  location: string;
  time: string;
}

interface RecentActivityProps {
  activities: Activity[];
}

export default function RecentActivity({ activities }: RecentActivityProps) {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-md transition-shadow">
      <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">Recent Activity</h2>
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <div key={index} className="flex items-start space-x-3 pb-4 border-b border-blue-100/50 last:border-0 last:pb-0">
            <div className={`w-2.5 h-2.5 rounded-full mt-2 shadow-sm ${
              activity.type === 'resolved' ? 'bg-emerald-500' :
              activity.type === 'active' ? 'bg-rose-500' : 'bg-amber-500'
            }`}></div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-blue-700 truncate">{activity.title}</p>
              <p className="text-xs text-blue-600/70 font-medium">{activity.location}</p>
              <p className="text-xs text-blue-500/60 mt-1">{activity.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

