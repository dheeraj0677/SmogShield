import { Leaf, ShieldPlus } from 'lucide-react';

export function ImpactMeter({ recommendations }) {
  if (!recommendations) return null;

  return (
    <section
      aria-label="Daily choice impact summary"
      className="rounded-2xl border border-teal-200 bg-gradient-to-r from-teal-50 via-emerald-50 to-sky-50 p-4 shadow-sm dark:border-teal-900 dark:from-teal-950/60 dark:via-emerald-950/40 dark:to-slate-900"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Your Direct Daily Impact Potential
          </h3>
          <p className="mt-0.5 text-xs text-slate-600 dark:text-slate-300">
            {recommendations.personalization_summary}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-2.5 rounded-xl border border-emerald-200 bg-white px-3.5 py-2 dark:border-emerald-800 dark:bg-slate-900">
            <ShieldPlus className="h-5 w-5 text-teal-600 dark:text-teal-400" aria-hidden="true" />
            <div>
              <p className="text-base font-extrabold text-slate-900 dark:text-white">
                -{recommendations.estimated_exposure_reduction_pct}%
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                PM2.5 Exposure
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 rounded-xl border border-emerald-200 bg-white px-3.5 py-2 dark:border-emerald-800 dark:bg-slate-900">
            <Leaf className="h-5 w-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
            <div>
              <p className="text-base font-extrabold text-slate-900 dark:text-white">
                {recommendations.total_potential_co2_saved_kg.toFixed(1)} kg
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                CO₂ Saved / Day
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
