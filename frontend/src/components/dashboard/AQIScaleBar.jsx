const EPA_SEGMENTS = [
  { label: 'Good', range: '0–50', color: 'bg-emerald-600', width: '10%' },
  { label: 'Moderate', range: '51–100', color: 'bg-amber-400', width: '10%' },
  { label: 'Sensitive', range: '101–150', color: 'bg-orange-500', width: '10%' },
  { label: 'Unhealthy', range: '151–200', color: 'bg-red-600', width: '10%' },
  { label: 'Very Unhealthy', range: '201–300', color: 'bg-purple-700', width: '20%' },
  { label: 'Hazardous', range: '301–500', color: 'bg-rose-900', width: '40%' },
];

export function AQIScaleBar({ aqi = 0 }) {
  const clamped = Math.max(0, Math.min(500, Number(aqi) || 0));
  const markerLeftPct = (clamped / 500) * 100;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="font-bold text-slate-900 dark:text-white">
          US EPA AQI Spectrum Scale
        </span>
        <span className="font-semibold text-teal-700 dark:text-teal-300">
          Current Marker: {clamped} / 500
        </span>
      </div>

      <div className="relative pt-3">
        <div
          className="absolute top-0 -translate-x-1/2 transition-all duration-700 ease-out"
          style={{ left: `${markerLeftPct}%` }}
          aria-hidden="true"
        >
          <div className="h-3 w-3 rotate-45 border-2 border-white bg-slate-900 shadow dark:border-slate-900 dark:bg-white" />
        </div>

        <div className="flex h-3 w-full overflow-hidden rounded-full shadow-inner">
          {EPA_SEGMENTS.map((seg) => (
            <div
              key={seg.label}
              className={`${seg.color} h-full`}
              style={{ width: seg.width }}
              title={`${seg.label} (${seg.range})`}
            />
          ))}
        </div>
      </div>

      <div className="mt-2 flex flex-wrap justify-between gap-2 text-[10px] font-medium text-slate-600 dark:text-slate-400">
        {EPA_SEGMENTS.map((seg) => (
          <span key={seg.label}>
            {seg.label} ({seg.range})
          </span>
        ))}
      </div>
    </div>
  );
}
