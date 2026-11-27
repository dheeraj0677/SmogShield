import { Leaf } from 'lucide-react';

export function AlternativesList({ alternatives = [] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {alternatives.map((alt) => (
        <article
          key={alt.id}
          className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div>
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                {alt.title}
              </h4>
              {alt.co2_saved_kg > 0 && (
                <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
                  <Leaf className="h-3 w-3" aria-hidden="true" />
                  {alt.co2_saved_kg} kg CO₂
                </span>
              )}
            </div>

            <p className="mt-2 text-xs leading-relaxed text-slate-700 dark:text-slate-300">
              {alt.description}
            </p>
          </div>

          <div className="mt-3 space-y-1.5 rounded-xl border border-emerald-200 bg-emerald-50/70 px-3 py-2 text-xs text-emerald-950 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200">
            <p className="font-semibold">{alt.impact_metric}</p>
            <p>{alt.impact}</p>
          </div>
        </article>
      ))}
    </div>
  );
}
