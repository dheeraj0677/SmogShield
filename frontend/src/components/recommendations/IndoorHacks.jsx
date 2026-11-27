import { Sparkles } from 'lucide-react';

export function IndoorHacks({ hacks = [], healthProtections = [] }) {
  const combined = [...healthProtections, ...hacks];

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {combined.map((item) => (
        <article
          key={item.id}
          className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div>
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                {item.title}
              </h4>
              <span className="shrink-0 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
                {item.impact_metric}
              </span>
            </div>

            <div className="mt-1.5 flex flex-wrap gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
              <span className="rounded bg-slate-100 px-2 py-0.5 capitalize dark:bg-slate-800">
                Cost: {item.cost}
              </span>
              <span className="rounded bg-slate-100 px-2 py-0.5 capitalize dark:bg-slate-800">
                Effort: {item.difficulty}
              </span>
              <span className="rounded bg-slate-100 px-2 py-0.5 dark:bg-slate-800">
                Best: {item.best_time}
              </span>
            </div>

            <p className="mt-2.5 text-xs leading-relaxed text-slate-700 dark:text-slate-300">
              {item.description}
            </p>
          </div>

          <div className="mt-3 rounded-xl bg-teal-50 px-3 py-2 text-xs text-teal-950 dark:bg-teal-950/40 dark:text-teal-200">
            <span className="inline-flex items-center gap-1 font-semibold">
              <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
              Direct Impact:
            </span>{' '}
            {item.impact}
          </div>
        </article>
      ))}
    </div>
  );
}
