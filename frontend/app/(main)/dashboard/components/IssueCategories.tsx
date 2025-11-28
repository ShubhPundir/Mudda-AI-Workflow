interface Category {
  category: string;
  count: number;
  percentage: number;
  gradient: string;
}

interface IssueCategoriesProps {
  categories: Category[];
}

export default function IssueCategories({ categories }: IssueCategoriesProps) {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-blue-100/50 p-6 hover:shadow-md transition-shadow">
      <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">Issue Categories</h2>
      <div className="space-y-4">
        {categories.map((item, index) => (
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
  );
}

