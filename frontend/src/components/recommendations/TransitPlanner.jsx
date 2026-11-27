import { useEffect, useState } from 'react';
import { Route, ShieldCheck } from 'lucide-react';
import { fetchCommutePlan } from '../../services/api.js';

export function TransitPlanner({ city }) {
  const [distanceKm, setDistanceKm] = useState(8);
  const [wearN95, setWearN95] = useState(true);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetchCommutePlan({
      city,
      distance_km: Number(distanceKm),
      wear_n95_mask: wearN95,
    })
      .then((data) => {
        if (active) setPlan(data);
      })
      .catch(() => {
        // Retain prior plan cleanly if rate-limited
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [city, distanceKm, wearN95]);

  const corridor = plan?.corridor_analysis;

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h4 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
              <Route className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
              Dijkstra Clean-Corridor Router &amp; Inhaled Dose Table
            </h4>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Optimizes your commute path by lowest cumulative PM2.5 inhalation rather than distance alone
            </p>
          </div>

          <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-800 dark:border-slate-700 dark:text-slate-200">
            <input
              type="checkbox"
              checked={wearN95}
              onChange={(e) => setWearN95(e.target.checked)}
              className="h-4 w-4 rounded text-teal-600"
            />
            Wearing N95/FFP2 Mask
          </label>
        </div>

        <div className="mt-3">
          <label
            htmlFor="commute-distance-slider"
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
          >
            One-Way Commute Distance: {distanceKm} km (Round trip: {distanceKm * 2} km)
          </label>
          <input
            id="commute-distance-slider"
            type="range"
            min={2}
            max={35}
            step={1}
            value={distanceKm}
            onChange={(e) => setDistanceKm(Number(e.target.value))}
            className="mt-1 w-full accent-teal-600"
          />
        </div>

        {corridor && (
          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50/70 p-3 dark:border-emerald-900 dark:bg-emerald-950/40">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-950 dark:text-emerald-200">
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                Recommended Clean Path ({corridor.cleanest_route.duration_min} min)
              </span>
              <span className="rounded-full bg-emerald-700 px-2.5 py-0.5 text-[11px] font-bold text-white">
                -{corridor.exposure_reduction_pct}% PM2.5 Dose ({corridor.pm25_dose_saved_ug} µg saved)
              </span>
            </div>
            <p className="mt-1.5 text-xs font-semibold text-slate-900 dark:text-white">
              {corridor.cleanest_route.path.join(' → ')}
            </p>
            <p className="mt-1 text-xs text-slate-700 dark:text-slate-300">
              {corridor.summary} (vs Arterial route: {corridor.standard_arterial.inhaled_pm25_ug} µg inhaled)
            </p>
          </div>
        )}
      </div>

      {plan?.mode_comparisons && (
        <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <table className="w-full text-left text-xs">
            <caption className="sr-only">
              Round-trip PM2.5 inhaled dose and CO2 emissions by commute mode
            </caption>
            <thead className="border-b border-slate-200 bg-slate-50 text-[11px] uppercase tracking-wide text-slate-600 dark:border-slate-800 dark:bg-slate-950/50 dark:text-slate-400">
              <tr>
                <th scope="col" className="px-4 py-3">Travel Mode</th>
                <th scope="col" className="px-3 py-3">Inhaled PM2.5</th>
                <th scope="col" className="px-3 py-3">CO₂ Emitted</th>
                <th scope="col" className="px-3 py-3">vs Peak</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {plan.mode_comparisons.map((row) => (
                <tr
                  key={row.mode}
                  className={row.recommended ? 'bg-teal-50/40 dark:bg-teal-950/20' : ''}
                >
                  <td className="px-4 py-2.5 font-semibold text-slate-900 dark:text-white">
                    {row.label}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-slate-800 dark:text-slate-200">
                    {row.inhaled_pm25_ug} µg
                  </td>
                  <td className="px-3 py-2.5 font-mono text-slate-800 dark:text-slate-200">
                    {row.co2_kg} kg
                  </td>
                  <td className="px-3 py-2.5">
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
                      -{row.exposure_vs_peak_pct}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading && (
            <p className="px-4 py-2 text-[11px] text-slate-500">Recalculating exposure...</p>
          )}
        </div>
      )}
    </div>
  );
}
