export function Footer() {
  return (
    <footer className="mt-10 border-t border-slate-200 bg-white py-6 text-xs text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
      <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-2 px-4 sm:flex-row sm:items-center sm:px-6">
        <p>
          <strong>SmogShield</strong> — Challenge 6: Urban Air Quality Assistant. Environmental &
          lifestyle guidance only; consult a physician for medical symptoms.
        </p>
        <p>Live data via WAQI / Open-Meteo &bull; US EPA AQI Standard (0–500)</p>
      </div>
    </footer>
  );
}
