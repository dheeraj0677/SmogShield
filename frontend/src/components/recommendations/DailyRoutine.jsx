import { Clock } from 'lucide-react';

const RISK_PILL = {
  low: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200',
  moderate: 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200',
  high: 'bg-orange-100 text-orange-900 dark:bg-orange-950 dark:text-orange-200',
  severe: 'bg-red-100 text-red-900 dark:bg-red-950 dark:text-red-200',
};

export function DailyRoutine({ schedule = [], routineItems = [] }) {
  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {schedule.map((slot) => (
          <article
            key={slot.time_window}
            className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
                <span className="text-xs font-bold uppercase tracking-wide text-teal-700 dark:text-teal-300">
                  {slot.time_window}
                </span>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  {slot.activity}
                </h4>
              </div>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold capitalize ${
                  RISK_PILL[slot.aqi_risk] || RISK_PILL.moderate
                }`}
              >
                {slot.aqi_risk} smog risk
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-800 dark:text-slate-200">
              {slot.recommended_action}
            </p>
            <div className="mt-2 flex flex-col gap-1 border-t border-slate-100 pt-2 text-xs text-slate-600 dark:border-slate-800 dark:text-slate-400 sm:flex-row sm:justify-between">
              <span>Why: {slot.rationale}</span>
              <span className="font-semibold text-emerald-700 dark:text-emerald-400">
                Impact: {slot.impact}
              </span>
            </div>
          </article>
        ))}
      </div>

      {routineItems.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {routineItems.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="flex items-start justify-between gap-2">
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  {item.title}
                </h4>
                <span className="shrink-0 rounded-full bg-teal-100 px-2 py-0.5 text-[11px] font-semibold text-teal-900 dark:bg-teal-950 dark:text-teal-200">
                  {item.impact_metric}
                </span>
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                {item.description}
              </p>
              <p className="mt-2 text-xs font-medium text-emerald-700 dark:text-emerald-400">
                Direct impact: {item.impact}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
