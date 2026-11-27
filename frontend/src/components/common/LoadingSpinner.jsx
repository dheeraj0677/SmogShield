export function LoadingSpinner({ label = 'Loading air quality insights...' }) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-3 py-10 text-slate-600 dark:text-slate-300"
      role="status"
      aria-live="polite"
    >
      <div
        className="h-9 w-9 animate-spin rounded-full border-4 border-teal-200 border-t-teal-600 dark:border-slate-700 dark:border-t-teal-400"
        aria-hidden="true"
      />
      <p className="text-sm font-medium">{label}</p>
    </div>
  );
}
