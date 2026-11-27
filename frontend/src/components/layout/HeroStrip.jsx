import { useRef } from 'react';
import {
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  Compass,
  Shield,
  Wind,
} from 'lucide-react';
import { getAQIMetadata } from '../../utils/aqiHelpers.js';

const HOTSPOT_CITIES = [
  { name: 'Delhi', region: 'Northern India', tag: 'Winter Inversion Watch' },
  { name: 'Lahore', region: 'Punjab Corridor', tag: 'Severe Smog Belt' },
  { name: 'Lucknow', region: 'Indo-Gangetic Plain', tag: 'Morning Haze Alert' },
  { name: 'Dhaka', region: 'Bengal Basin', tag: 'Urban Particulate Peak' },
  { name: 'Beijing', region: 'North China Plain', tag: 'Regional Monitoring' },
  { name: 'London', region: 'Thames Valley', tag: 'Clean Air Benchmark' },
];

export function HeroStrip({ city, aqiSnapshot, onSelectCity }) {
  const scrollerRef = useRef(null);
  const aqi = aqiSnapshot?.aqi ?? 150;
  const meta = getAQIMetadata(aqi);

  const heroGradient =
    aqi <= 50
      ? 'from-emerald-900 via-teal-800 to-cyan-900'
      : aqi <= 100
        ? 'from-slate-900 via-amber-900 to-teal-900'
        : aqi <= 200
          ? 'from-slate-950 via-orange-950 to-slate-900'
          : 'from-slate-950 via-rose-950 to-purple-950';

  const scrollCarousel = (direction) => {
    if (!scrollerRef.current) return;
    if (typeof scrollerRef.current.scrollBy === 'function') {
      scrollerRef.current.scrollBy({
        left: direction * 240,
        behavior: 'smooth',
      });
    } else {
      scrollerRef.current.scrollLeft += direction * 240;
    }
  };

  return (
    <section
      aria-label="Live air quality overview and quick navigation"
      className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${heroGradient} p-5 text-white shadow-lg sm:p-6`}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-20 mix-blend-luminosity"
        aria-hidden="true"
      >
        <img
          src="/images/hero-smog-skyline.jpg"
          alt=""
          className="h-full w-full object-cover object-center"
        />
      </div>
      <div
        className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-teal-400/20 blur-3xl animate-float-slow"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute -bottom-20 left-1/3 h-56 w-56 rounded-full bg-sky-400/10 blur-3xl"
        aria-hidden="true"
      />

      <div className="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2.5">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold backdrop-blur-sm">
            <Shield className="h-3.5 w-3.5 text-teal-300" aria-hidden="true" />
            <span>Live Winter Smog Shield &bull; {aqiSnapshot?.resolved_city || city}</span>
          </div>

          <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl">
            Protect your family&apos;s lungs today
          </h2>

          <p className="max-w-2xl text-xs leading-relaxed text-slate-200 sm:text-sm">
            {aqiSnapshot?.weather?.dispersion_note ||
              'Real-time pollution telemetry, room-level air filtration sizing, and low-emission routines tailored to your household.'}
          </p>

          <nav aria-label="Quick section jump links" className="flex flex-wrap gap-2 pt-1">
            {[
              { href: '#overview', label: 'Live Telemetry & AI' },
              { href: '#visual-guides', label: 'Visual Playbooks' },
              { href: '#trend-section', label: '24h Smog Curve' },
              { href: '#action-plans', label: 'Action Plans & Solvers' },
            ].map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="inline-flex items-center gap-1 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold text-white transition hover:bg-white/20"
              >
                <ArrowDown className="h-3 w-3" aria-hidden="true" />
                {link.label}
              </a>
            ))}
          </nav>
        </div>

        <div className="flex shrink-0 items-center gap-4 rounded-2xl border border-white/20 bg-white/10 px-4 py-3 backdrop-blur-md">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-300">
              Current Index
            </p>
            <p className="text-3xl font-black tracking-tight">{aqiSnapshot?.aqi ?? '—'}</p>
            <span className={`mt-1 inline-block rounded-full px-2.5 py-0.5 text-[11px] font-bold ${meta.badgeClass}`}>
              {meta.label}
            </span>
          </div>
          <div className="h-12 w-px bg-white/20" aria-hidden="true" />
          <div className="space-y-1 text-xs text-slate-200">
            <p className="flex items-center gap-1.5 font-semibold">
              <Wind className="h-3.5 w-3.5 text-teal-300" aria-hidden="true" />
              {aqiSnapshot?.weather?.wind_speed_kmh != null
                ? `${aqiSnapshot.weather.wind_speed_kmh} km/h wind`
                : 'Monitoring wind'}
            </p>
            <p>
              PM2.5:{' '}
              <strong className="text-white">
                {aqiSnapshot?.pollutants?.pm25 != null ? `${aqiSnapshot.pollutants.pm25} µg/m³` : '—'}
              </strong>
            </p>
            <p className="text-[11px] text-slate-300">
              Trapping risk: <strong className="uppercase">{aqiSnapshot?.weather?.smog_trapping_risk || 'moderate'}</strong>
            </p>
          </div>
        </div>
      </div>

      {/* Horizontal scrollable city hotspot carousel */}
      <div className="relative mt-5 border-t border-white/15 pt-4">
        <div className="mb-2 flex items-center justify-between">
          <p className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
            <Compass className="h-3.5 w-3.5 text-teal-300" aria-hidden="true" />
            Scroll Urban Smog Hotspots
          </p>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => scrollCarousel(-1)}
              aria-label="Scroll hotspot cities left"
              className="rounded-lg border border-white/20 bg-white/10 p-1 text-white transition hover:bg-white/20"
            >
              <ChevronLeft className="h-4 w-4" aria-hidden="true" />
            </button>
            <button
              type="button"
              onClick={() => scrollCarousel(1)}
              aria-label="Scroll hotspot cities right"
              className="rounded-lg border border-white/20 bg-white/10 p-1 text-white transition hover:bg-white/20"
            >
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>

        <div
          ref={scrollerRef}
          className="custom-scrollbar flex snap-x snap-mandatory gap-2.5 overflow-x-auto pb-1.5"
        >
          {HOTSPOT_CITIES.map((item) => {
            const active = item.name.toLowerCase() === city.toLowerCase();
            return (
              <button
                key={item.name}
                type="button"
                onClick={() => onSelectCity(item.name)}
                aria-pressed={active}
                className={`min-w-[170px] shrink-0 snap-start rounded-2xl border px-3.5 py-2.5 text-left transition ${
                  active
                    ? 'border-teal-300 bg-teal-500/30 shadow-md'
                    : 'border-white/15 bg-white/10 hover:bg-white/20'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-bold text-white">{item.name}</span>
                  {active && (
                    <span className="rounded-full bg-teal-300 px-2 py-0.5 text-[10px] font-bold text-slate-950">
                      Active
                    </span>
                  )}
                </div>
                <p className="mt-0.5 text-[11px] text-slate-200">{item.region}</p>
                <p className="mt-1 text-[10px] font-medium text-teal-200">{item.tag}</p>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
