import { RefreshCw } from 'lucide-react';
import { AQIGauge } from './AQIGauge.jsx';
import { HealthTips } from './HealthTips.jsx';
import { PollutantCards } from './PollutantCards.jsx';
import { SmogSparkline } from './SmogSparkline.jsx';
import { WeatherCard } from './WeatherCard.jsx';

export function AQIDashboard({ snapshot, recommendations, loading, onRefresh }) {
  if (!snapshot) return null;

  return (
    <section aria-label="Live Air Quality Dashboard" className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {snapshot.resolved_city}
            {snapshot.country ? `, ${snapshot.country}` : ''}
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Source: <span className="font-medium uppercase">{snapshot.data_source}</span>
            {snapshot.cached ? ' (cached)' : ' (live)'}
          </p>
        </div>

        <button
          type="button"
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
          Refresh Live AQI
        </button>
      </div>

      {recommendations && (
        <HealthTips
          effectiveAqi={recommendations.effective_aqi}
          alertMessage={recommendations.alert_message}
        />
      )}

      <div className="grid gap-4 md:grid-cols-12">
        <div className="space-y-4 md:col-span-5">
          <AQIGauge
            aqi={snapshot.aqi}
            city={snapshot.resolved_city}
            dominantPollutant={snapshot.dominant_pollutant}
          />
          <WeatherCard weather={snapshot.weather} />
        </div>

        <div className="md:col-span-7">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <h3 className="mb-3 text-sm font-bold text-slate-900 dark:text-white">
              Pollutant Breakdown
            </h3>
            <PollutantCards
              pollutants={snapshot.pollutants}
              dominantPollutant={snapshot.dominant_pollutant}
            />
          </div>
        </div>
      </div>

      <SmogSparkline trend={snapshot.hourly_trend} city={snapshot.resolved_city} />
    </section>
  );
}
