import { memo } from 'react';
import { Activity } from 'lucide-react';

function SmogSparklineBase({ trend = [], city = '' }) {
  if (!trend || trend.length < 2) return null;

  const width = 460;
  const height = 110;
  const padX = 12;
  const padY = 14;

  const values = trend.map((pt) => Number(pt.aqi) || 0);
  const maxVal = Math.max(100, ...values);
  const minVal = Math.max(0, Math.min(...values) - 10);
  const span = Math.max(10, maxVal - minVal);

  const coords = trend.map((pt, idx) => {
    const x = padX + (idx / (trend.length - 1)) * (width - padX * 2);
    const y = height - padY - (((Number(pt.aqi) || 0) - minVal) / span) * (height - padY * 2);
    return { x, y, ...pt };
  });

  const polylinePoints = coords.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  const peakPoint = coords.reduce((best, cur) => (cur.aqi > best.aqi ? cur : best), coords[0]);
  const safestPoint = coords.reduce((best, cur) => (cur.aqi < best.aqi ? cur : best), coords[0]);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
          <Activity className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
          24-Hour Diurnal Smog Cycle
        </h3>
        <div className="flex flex-wrap gap-2 text-[11px]">
          <span className="rounded-full bg-red-100 px-2 py-0.5 font-semibold text-red-900 dark:bg-red-950 dark:text-red-200">
            Peak: {peakPoint.hour} (AQI {peakPoint.aqi})
          </span>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 font-semibold text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
            Safest Window: {safestPoint.hour} (AQI {safestPoint.aqi})
          </span>
        </div>
      </div>

      <div className="mt-3 overflow-hidden rounded-xl bg-slate-50 p-2 dark:bg-slate-950/60">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-28 w-full"
          role="img"
          aria-label={`24-hour diurnal AQI trend for ${city}`}
        >
          <polyline
            fill="none"
            stroke="#0d9488"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={polylinePoints}
          />
          {coords.map((p) => (
            <circle
              key={p.hour}
              cx={p.x}
              cy={p.y}
              r={p.hour === peakPoint.hour || p.hour === safestPoint.hour ? 4.5 : 2.5}
              fill={
                p.hour === peakPoint.hour
                  ? '#dc2626'
                  : p.hour === safestPoint.hour
                    ? '#15803d'
                    : '#0d9488'
              }
            />
          ))}
        </svg>

        <div className="mt-1 flex justify-between px-1 text-[10px] font-medium text-slate-500 dark:text-slate-400">
          <span>{coords[0].hour}</span>
          <span>{coords[Math.floor(coords.length / 2)].hour}</span>
          <span>{coords[coords.length - 1].hour}</span>
        </div>
      </div>

      {/* Twin representation for screen readers */}
      <div className="sr-only">
        <h4>Hourly AQI breakdown for {city}</h4>
        <ul>
          {trend.map((pt) => (
            <li key={pt.hour}>
              At {pt.hour}: AQI {pt.aqi}, PM2.5 {pt.pm25} micrograms per cubic meter.
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export const SmogSparkline = memo(SmogSparklineBase);
