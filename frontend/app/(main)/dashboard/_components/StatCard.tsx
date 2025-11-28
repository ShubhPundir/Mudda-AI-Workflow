interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
  gradient: string;
}

export default function StatCard({ title, value, subtitle, icon, color, gradient }: StatCardProps) {
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
}

