import { useEffect, useState } from 'react';
import { Fan, Gauge } from 'lucide-react';
import { calculateRoomCADR } from '../../services/api.js';

const PRESET_FILTERS = [
  { label: 'DIY Box-Fan (240 m³/h)', cadr: 240 },
  { label: 'Bedroom HEPA (310 m³/h)', cadr: 310 },
  { label: 'Living Room HEPA (480 m³/h)', cadr: 480 },
];

export function CADRCalculator({ outdoorPm25 = 160 }) {
  const [roomArea, setRoomArea] = useState(160);
  const [ceilingHeight, setCeilingHeight] = useState(9.5);
  const [cadr, setCadr] = useState(240);
  const [sealQuality, setSealQuality] = useState('average');
  const [result, setResult] = useState(null);

  useEffect(() => {
    let active = true;
    calculateRoomCADR({
      room_area_sqft: Number(roomArea),
      ceiling_height_ft: Number(ceilingHeight),
      outdoor_pm25: Number(outdoorPm25) || 150,
      purifier_cadr_m3h: Number(cadr),
      seal_quality: sealQuality,
    })
      .then((data) => {
        if (active) setResult(data);
      })
      .catch(() => {
        // Ignore transient errors while sliding sliders
      });
    return () => {
      active = false;
    };
  }, [roomArea, ceilingHeight, outdoorPm25, cadr, sealQuality]);

  return (
    <section
      aria-label="Room CADR and Air Change Calculator"
      className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h4 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
            <Fan className="h-4 w-4 text-teal-600 dark:text-teal-400" aria-hidden="true" />
            Room CADR &amp; Clean-Air Decay Solver
          </h4>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Sizes your HEPA or DIY box-fan filter to hit the 4.8 ACH clean-room standard
          </p>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {PRESET_FILTERS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => setCadr(preset.cadr)}
              aria-pressed={cadr === preset.cadr}
              className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
                cadr === preset.cadr
                  ? 'bg-teal-700 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div>
          <label
            htmlFor="cadr-area-input"
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
          >
            Room Area: {roomArea} sq ft
          </label>
          <input
            id="cadr-area-input"
            type="range"
            min={80}
            max={600}
            step={10}
            value={roomArea}
            onChange={(e) => setRoomArea(Number(e.target.value))}
            className="mt-1 w-full accent-teal-600"
          />
        </div>

        <div>
          <label
            htmlFor="cadr-power-input"
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
          >
            Purifier CADR: {cadr} m³/h
          </label>
          <input
            id="cadr-power-input"
            type="range"
            min={80}
            max={700}
            step={10}
            value={cadr}
            onChange={(e) => setCadr(Number(e.target.value))}
            className="mt-1 w-full accent-teal-600"
          />
        </div>

        <div>
          <label
            htmlFor="cadr-seal-select"
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
          >
            Window / Door Seal
          </label>
          <select
            id="cadr-seal-select"
            value={sealQuality}
            onChange={(e) => setSealQuality(e.target.value)}
            className="mt-1 w-full rounded-xl border border-slate-300 bg-slate-50 px-2.5 py-1.5 text-xs text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          >
            <option value="tight">Tight Weatherstripping</option>
            <option value="average">Average Urban Room</option>
            <option value="leaky">Drafty / Older Windows</option>
          </select>
        </div>
      </div>

      <div className="mt-2 hidden">
        <label htmlFor="cadr-height-input">Ceiling Height</label>
        <input
          id="cadr-height-input"
          type="number"
          value={ceilingHeight}
          onChange={(e) => setCeilingHeight(Number(e.target.value))}
        />
      </div>

      {result && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800/70">
          <div className="grid grid-cols-2 gap-3 text-center sm:grid-cols-4">
            <div>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {result.ach} ACH
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">Air Changes/Hr</p>
            </div>
            <div>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {result.minutes_to_safe_air} min
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">To &lt;15 µg/m³</p>
            </div>
            <div>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {result.projected_steady_pm25} µg/m³
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">Steady Indoor PM2.5</p>
            </div>
            <div>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {result.recommended_cadr_m3h} m³/h
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">Target CADR (4.8 ACH)</p>
            </div>
          </div>

          <p className="mt-2.5 flex items-center gap-1.5 text-xs font-medium text-teal-800 dark:text-teal-300">
            <Gauge className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{result.efficiency_note}</span>
          </p>
        </div>
      )}
    </section>
  );
}
