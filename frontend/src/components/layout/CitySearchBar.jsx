import { useState } from 'react';
import { MapPin, Search } from 'lucide-react';
import { POPULAR_CITIES } from '../../utils/constants.js';
import { sanitizeDisplayCity } from '../../utils/accessibility.js';

export function CitySearchBar({ city, onCityChange, onUseGeolocation, locating }) {
  const [query, setQuery] = useState(city);

  const handleSubmit = (event) => {
    event.preventDefault();
    const cleaned = sanitizeDisplayCity(query);
    if (cleaned.length >= 2) {
      onCityChange(cleaned);
    }
  };

  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
      <form
        onSubmit={handleSubmit}
        className="flex flex-1 items-center gap-2"
        role="search"
        aria-label="City air quality lookup"
      >
        <label htmlFor="city-search-input" className="sr-only">
          Enter city name
        </label>
        <div className="relative flex-1 sm:w-52">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <input
            id="city-search-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search city (e.g. Delhi, Lahore)"
            maxLength={80}
            className="w-full rounded-xl border border-slate-300 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-500 focus:border-teal-600 focus:bg-white dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-400"
          />
        </div>
        <button
          type="submit"
          className="rounded-xl bg-teal-700 px-3.5 py-2 text-sm font-semibold text-white transition hover:bg-teal-800"
        >
          Check
        </button>
        <button
          type="button"
          onClick={onUseGeolocation}
          disabled={locating}
          aria-label="GPS — Use my current location"
          title="Use my current location"
          className="inline-flex items-center gap-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          <MapPin className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
          <span className="hidden sm:inline">{locating ? 'Locating...' : 'GPS'}</span>
        </button>
      </form>

      <div className="flex flex-wrap items-center gap-1.5">
        {POPULAR_CITIES.map((preset) => {
          const active = preset.toLowerCase() === city.toLowerCase();
          return (
            <button
              key={preset}
              type="button"
              onClick={() => {
                setQuery(preset);
                onCityChange(preset);
              }}
              aria-pressed={active}
              className={`rounded-full px-2.5 py-1 text-xs font-medium transition ${
                active
                  ? 'bg-teal-700 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
              }`}
            >
              {preset}
            </button>
          );
        })}
      </div>
    </div>
  );
}
