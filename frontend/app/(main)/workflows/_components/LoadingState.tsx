export default function LoadingState() {
  return (
    <div className="text-center py-16">
      <div className="inline-block relative">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-6 h-6 bg-primary-100 rounded-full"></div>
        </div>
      </div>
      <p className="mt-4 text-gray-600 font-medium">Loading workflows...</p>
    </div>
  );
}

