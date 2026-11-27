import { getAQIMetadata } from '../../utils/aqiHelpers.js';

export function AQIGauge({ aqi, city, dominantPollutant }) {
  const clamped = Math.max(0, Math.min(500, Number(aqi) || 0));
  const meta = getAQIMetadata(clamped);
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const pct = clamped / 500;
  const strokeDashoffset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div
        role="meter"
        aria-label={`Air Quality Index for ${city}`}
        aria-valuemin={0}
        aria-valuemax={500}
        aria-valuenow={clamped}
        aria-valuetext={`AQI ${clamped}, ${meta.label}`}
        className="relative flex h-36 w-36 items-center justify-center"
      >
        <svg className="h-36 w-36 -rotate-90" viewBox="0 0 140 140" aria-hidden="true">
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="12"
            className="text-slate-200 dark:text-slate-800"
          />
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke={meta.ringColor}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            {clamped}
          </span>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            US AQI
          </span>
        </div>
      </div>

      <span className={`mt-3 rounded-full px-3 py-1 text-xs font-bold ${meta.badgeClass}`}>
        {meta.label}
      </span>

      <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">
        Primary driver:{' '}
        <strong className="uppercase text-slate-900 dark:text-slate-200">
          {dominantPollutant || 'PM2.5'}
        </strong>
      </p>
    </div>
  );
}
