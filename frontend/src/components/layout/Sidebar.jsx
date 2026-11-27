import { HeartHandshake, Home, ShieldAlert, Users, X } from 'lucide-react';
import {
  BUDGET_OPTIONS,
  COMMUTE_OPTIONS,
  HEALTH_CONDITION_OPTIONS,
  HOME_TYPE_OPTIONS,
} from '../../utils/constants.js';

export function Sidebar({ profile, onChangeProfile, openMobile, onCloseMobile }) {
  const toggleCondition = (id) => {
    const exists = profile.health_conditions.includes(id);
    const next = exists
      ? profile.health_conditions.filter((item) => item !== id)
      : [...profile.health_conditions, id];
    onChangeProfile({ ...profile, health_conditions: next });
  };

  return (
    <aside
      aria-label="Household context settings"
      className={`${
        openMobile
          ? 'fixed inset-0 z-40 flex bg-slate-950/60 backdrop-blur-sm lg:static lg:block lg:bg-transparent lg:backdrop-blur-none'
          : 'hidden lg:sticky lg:top-20 lg:block'
      }`}
    >
      <div className="custom-scrollbar h-full w-80 overflow-y-auto border-r border-slate-200 bg-white p-5 shadow-xl lg:max-h-[calc(100vh-6rem)] lg:w-full lg:rounded-2xl lg:border lg:shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-teal-600 dark:text-teal-400" aria-hidden="true" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Household Context
            </h2>
          </div>
          <button
            type="button"
            onClick={onCloseMobile}
            aria-label="Close household context drawer"
            className="rounded-lg p-1 text-slate-500 hover:bg-slate-100 lg:hidden dark:text-slate-400 dark:hover:bg-slate-800"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">
          Tailors AQI risk thresholds, daily routines, indoor hacks, and AI advice to your family.
        </p>

        <div className="mt-4 space-y-4">
          <div>
            <label
              htmlFor="family-members-input"
              className="block text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
            >
              Family Members: {profile.family_members}
            </label>
            <input
              id="family-members-input"
              type="range"
              min={1}
              max={10}
              value={profile.family_members}
              onChange={(e) =>
                onChangeProfile({ ...profile, family_members: Number(e.target.value) })
              }
              className="mt-1.5 w-full accent-teal-600"
            />
          </div>

          <fieldset className="space-y-2">
            <legend className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">
              <ShieldAlert className="h-3.5 w-3.5 text-amber-600" aria-hidden="true" />
              Sensitive Groups
            </legend>
            <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-800 dark:text-slate-200">
              <input
                type="checkbox"
                checked={profile.has_children}
                onChange={(e) =>
                  onChangeProfile({ ...profile, has_children: e.target.checked })
                }
                className="h-4 w-4 rounded border-slate-300 text-teal-600"
              />
              Children in household
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-800 dark:text-slate-200">
              <input
                type="checkbox"
                checked={profile.has_elderly}
                onChange={(e) =>
                  onChangeProfile({ ...profile, has_elderly: e.target.checked })
                }
                className="h-4 w-4 rounded border-slate-300 text-teal-600"
              />
              Elderly adults (65+)
            </label>
          </fieldset>

          <fieldset>
            <legend className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">
              <HeartHandshake className="h-3.5 w-3.5 text-rose-600" aria-hidden="true" />
              Health Sensitivities
            </legend>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {HEALTH_CONDITION_OPTIONS.map((opt) => {
                const selected = profile.health_conditions.includes(opt.id);
                return (
                  <button
                    key={opt.id}
                    type="button"
                    aria-pressed={selected}
                    onClick={() => toggleCondition(opt.id)}
                    className={`rounded-lg border px-2.5 py-1 text-xs font-medium transition ${
                      selected
                        ? 'border-teal-600 bg-teal-50 text-teal-800 dark:border-teal-500 dark:bg-teal-950/60 dark:text-teal-200'
                        : 'border-slate-300 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
                    }`}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </fieldset>

          <div>
            <label
              htmlFor="commute-select"
              className="block text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
            >
              Primary Commute
            </label>
            <select
              id="commute-select"
              value={profile.commute_type}
              onChange={(e) => onChangeProfile({ ...profile, commute_type: e.target.value })}
              className="mt-1.5 w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            >
              {COMMUTE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              htmlFor="home-type-select"
              className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
            >
              <Home className="h-3.5 w-3.5 text-teal-600" aria-hidden="true" />
              Home Environment
            </label>
            <select
              id="home-type-select"
              value={profile.home_type}
              onChange={(e) => onChangeProfile({ ...profile, home_type: e.target.value })}
              className="mt-1.5 w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            >
              {HOME_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <label className="mt-2.5 flex cursor-pointer items-center gap-2 text-sm text-slate-800 dark:text-slate-200">
              <input
                type="checkbox"
                checked={profile.has_air_purifier}
                onChange={(e) =>
                  onChangeProfile({ ...profile, has_air_purifier: e.target.checked })
                }
                className="h-4 w-4 rounded border-slate-300 text-teal-600"
              />
              Already own a HEPA purifier
            </label>
          </div>

          <div>
            <label
              htmlFor="budget-select"
              className="block text-xs font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300"
            >
              Intervention Budget
            </label>
            <select
              id="budget-select"
              value={profile.budget}
              onChange={(e) => onChangeProfile({ ...profile, budget: e.target.value })}
              className="mt-1.5 w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            >
              {BUDGET_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </aside>
  );
}
