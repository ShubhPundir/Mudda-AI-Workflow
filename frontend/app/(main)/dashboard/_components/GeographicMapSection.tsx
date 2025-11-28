import GeographicMap from '@/components/GeographicMap';

interface IssueLocation {
  id: string;
  lat: number;
  lng: number;
  status: 'active' | 'resolved' | 'pending';
  title: string;
}

interface GeographicMapSectionProps {
  issues: IssueLocation[];
}

export default function GeographicMapSection({ issues }: GeographicMapSectionProps) {
  return (
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
        <GeographicMap issues={issues} height="500px" />
      </div>
    </div>
  );
}

