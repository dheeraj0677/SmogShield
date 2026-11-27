import { CloudFog, Droplets, Thermometer, Wind } from 'lucide-react';

export function WeatherCard({ weather }) {
  if (!weather) return null;

  const riskBadge =
    weather.smog_trapping_risk === 'high'
      ? 'bg-red-100 text-red-900 dark:bg-red-950/70 dark:text-red-200'
      : weather.smog_trapping_risk === 'moderate'
        ? 'bg-amber-100 text-amber-900 dark:bg-amber-950/70 dark:text-amber-200'
        : 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/70 dark:text-emerald-200';

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between gap-2">
        <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
          <CloudFog className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
          Smog Meteorology
        </h3>
        <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold capitalize ${riskBadge}`}>
          {weather.smog_trapping_risk} trapping risk
        </span>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/70">
          <Thermometer className="mx-auto h-4 w-4 text-orange-500" aria-hidden="true" />
          <p className="mt-1 text-sm font-bold text-slate-900 dark:text-white">
            {weather.temperature_c != null ? `${weather.temperature_c}°C` : '—'}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Temp</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/70">
          <Droplets className="mx-auto h-4 w-4 text-sky-500" aria-hidden="true" />
          <p className="mt-1 text-sm font-bold text-slate-900 dark:text-white">
            {weather.humidity_pct != null ? `${weather.humidity_pct}%` : '—'}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Humidity</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/70">
          <Wind className="mx-auto h-4 w-4 text-teal-500" aria-hidden="true" />
          <p className="mt-1 text-sm font-bold text-slate-900 dark:text-white">
            {weather.wind_speed_kmh != null ? `${weather.wind_speed_kmh} km/h` : '—'}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Wind</p>
        </div>
      </div>

      {weather.dispersion_note && (
        <p className="mt-3 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
          <strong>{weather.condition}:</strong> {weather.dispersion_note}
        </p>
      )}
    </div>
  );
}
