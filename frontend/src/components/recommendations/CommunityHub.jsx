import { useState } from 'react';
import { CheckSquare, Globe2, Square, Users2 } from 'lucide-react';
import { useLocalStorage } from '../../hooks/useLocalStorage.js';
import { ADVISORY_TRANSLATIONS, COMMUNITY_PLEDGES } from '../../utils/translations.js';

export function CommunityHub({ effectiveAqi = 180 }) {
  const [lang, setLang] = useState('en');
  const [pledgedIds, setPledgedIds] = useLocalStorage('smogshield_pledges_v1', [
    'pledge-zero-burn',
  ]);

  const togglePledge = (id) => {
    setPledgedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const activePledges = COMMUNITY_PLEDGES.filter((p) => pledgedIds.includes(p.id));
  const totalCo2 = activePledges.reduce((acc, p) => acc + p.co2_kg_saved, 0);
  const totalPmAvoided = activePledges.reduce((acc, p) => acc + p.pm25_g_prevented, 0);

  const t = ADVISORY_TRANSLATIONS[lang] || ADVISORY_TRANSLATIONS.en;
  const severityKey = effectiveAqi <= 50 ? 'good' : effectiveAqi <= 100 ? 'moderate' : 'high';

  return (
    <div className="space-y-4">
      <section
        aria-label="Multilingual emergency smog advisory"
        dir={t.dir}
        className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <div className="flex flex-wrap items-center justify-between gap-2" dir="ltr">
          <h4 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
            <Globe2 className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
            Multilingual Community Advisory
          </h4>
          <div className="flex flex-wrap gap-1.5" role="group" aria-label="Select advisory language">
            {Object.entries(ADVISORY_TRANSLATIONS).map(([code, item]) => (
              <button
                key={code}
                type="button"
                aria-pressed={lang === code}
                onClick={() => setLang(code)}
                className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
                  lang === code
                    ? 'bg-teal-700 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-3 rounded-xl border border-teal-200 bg-teal-50/70 p-3.5 dark:border-teal-900 dark:bg-teal-950/40">
          <h5 className="text-sm font-bold text-teal-950 dark:text-teal-100">{t.heading}</h5>
          <p className="mt-1.5 text-sm leading-relaxed text-slate-800 dark:text-slate-200">
            {t[severityKey]}
          </p>
        </div>
      </section>

      <section
        aria-label="Neighborhood emission reduction pledges"
        className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h4 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
            <Users2 className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
            Neighborhood Clean-Air Pledges
          </h4>
          <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
            {totalCo2.toFixed(1)} kg CO₂ &amp; {totalPmAvoided}g PM2.5 prevented/day
          </span>
        </div>

        <div className="mt-3 grid gap-2.5 sm:grid-cols-2">
          {COMMUNITY_PLEDGES.map((pledge) => {
            const checked = pledgedIds.includes(pledge.id);
            return (
              <button
                key={pledge.id}
                type="button"
                aria-pressed={checked}
                onClick={() => togglePledge(pledge.id)}
                className={`flex items-start gap-2.5 rounded-xl border p-3 text-left transition ${
                  checked
                    ? 'border-teal-600 bg-teal-50/60 dark:border-teal-500 dark:bg-teal-950/40'
                    : 'border-slate-200 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800'
                }`}
              >
                {checked ? (
                  <CheckSquare className="mt-0.5 h-4 w-4 shrink-0 text-teal-700 dark:text-teal-400" aria-hidden="true" />
                ) : (
                  <Square className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
                )}
                <div>
                  <p className="text-xs font-bold text-slate-900 dark:text-white">{pledge.title}</p>
                  <p className="mt-1 text-[11px] text-slate-600 dark:text-slate-300">
                    {pledge.description}
                  </p>
                  <p className="mt-1.5 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400">
                    Impact: -{pledge.co2_kg_saved} kg CO₂ &amp; -{pledge.pm25_g_prevented}g local soot
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}
