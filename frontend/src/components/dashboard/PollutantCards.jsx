import { POLLUTANT_LABELS } from '../../utils/aqiHelpers.js';

export function PollutantCards({ pollutants = {}, dominantPollutant = 'pm25' }) {
  const entries = Object.entries(POLLUTANT_LABELS);

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {entries.map(([key, meta]) => {
        const value = pollutants?.[key];
        const hasVal = typeof value === 'number' && !Number.isNaN(value);
        const ratio = hasVal ? Math.min(100, Math.round((value / meta.limit) * 100)) : 0;
        const isDominant = dominantPollutant?.toLowerCase() === key;

        return (
          <div
            key={key}
            className={`rounded-xl border p-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${
              isDominant
                ? 'border-teal-500 bg-teal-50/60 shadow-sm dark:border-teal-600 dark:bg-teal-950/35'
                : 'border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900'
            }`}
          >
            <div className="flex items-center justify-between gap-1">
              <span className="text-xs font-bold text-slate-900 dark:text-white">
                {meta.label}
              </span>
              {isDominant && (
                <span className="rounded bg-teal-700 px-1.5 py-0.5 text-[10px] font-semibold text-white">
                  Main
                </span>
              )}
            </div>

            <p className="mt-1.5 text-lg font-extrabold text-slate-900 dark:text-slate-100">
              {hasVal ? value : '—'}{' '}
              <span className="text-xs font-normal text-slate-500 dark:text-slate-400">
                {meta.unit}
              </span>
            </p>

            <div
              className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800"
              aria-hidden="true"
            >
              <div
                className={`h-full rounded-full ${
                  ratio >= 100
                    ? 'bg-red-600'
                    : ratio >= 60
                      ? 'bg-amber-500'
                      : 'bg-teal-600'
                }`}
                style={{ width: `${ratio}%` }}
              />
            </div>

            <p className="mt-1.5 text-[11px] text-slate-600 dark:text-slate-400">
              {meta.detail}
            </p>
          </div>
        );
      })}
    </div>
  );
}
