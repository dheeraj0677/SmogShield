import { Moon, ShieldCheck, SlidersHorizontal, Sun, Type } from 'lucide-react';
import { getAQIMetadata } from '../../utils/aqiHelpers.js';
import { CitySearchBar } from './CitySearchBar.jsx';

export function Header({
  city,
  onCityChange,
  onUseGeolocation,
  locating,
  aqiSnapshot,
  darkMode = false,
  onToggleDarkMode,
  largeText = false,
  onToggleLargeText,
  onToggleSidebar,
}) {
  const aqiMeta = aqiSnapshot ? getAQIMetadata(aqiSnapshot.aqi) : null;

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/90">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-700 text-white shadow-sm">
              <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">
                SmogShield
              </h1>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                GenAI Urban Air Quality &amp; Family Advisor
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 lg:hidden">
            <button
              type="button"
              onClick={onToggleSidebar}
              aria-label="Open household context settings"
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
              Profile
            </button>
            {onToggleLargeText && (
              <button
                type="button"
                onClick={onToggleLargeText}
                aria-pressed={largeText}
                aria-label="Aa+ — Toggle large readable text"
                className={`rounded-lg border px-2 py-1.5 text-xs font-bold ${
                  largeText
                    ? 'border-teal-600 bg-teal-700 text-white'
                    : 'border-slate-300 text-slate-700 dark:border-slate-700 dark:text-slate-200'
                }`}
              >
                Aa+
              </button>
            )}
            <button
              type="button"
              onClick={onToggleDarkMode}
              aria-pressed={darkMode}
              aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              className="rounded-lg border border-slate-300 p-2 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              {darkMode ? (
                <Sun className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Moon className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        <CitySearchBar
          city={city}
          onCityChange={onCityChange}
          onUseGeolocation={onUseGeolocation}
          locating={locating}
        />

        <div className="hidden items-center gap-2 lg:flex">
          {aqiSnapshot && aqiMeta && (
            <div
              className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${aqiMeta.badgeClass}`}
              aria-label={`Current AQI ${aqiSnapshot.aqi} ${aqiMeta.label}`}
            >
              <span>AQI {aqiSnapshot.aqi}</span>
              <span>•</span>
              <span>{aqiMeta.label}</span>
            </div>
          )}

          {onToggleLargeText && (
            <button
              type="button"
              onClick={onToggleLargeText}
              aria-pressed={largeText}
              aria-label="Aa+ — Toggle large readable text"
              title="Large text accessibility mode"
              className={`inline-flex items-center gap-1 rounded-xl border px-2.5 py-2 text-xs font-bold transition ${
                largeText
                  ? 'border-teal-600 bg-teal-700 text-white'
                  : 'border-slate-300 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800'
              }`}
            >
              <Type className="h-3.5 w-3.5" aria-hidden="true" />
              <span>Aa+</span>
            </button>
          )}

          <button
            type="button"
            onClick={onToggleDarkMode}
            aria-pressed={darkMode}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 px-2.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            {darkMode ? (
              <>
                <Sun className="h-4 w-4" aria-hidden="true" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon className="h-4 w-4" aria-hidden="true" />
                <span>Dark</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
