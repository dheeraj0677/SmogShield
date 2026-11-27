import { AlertTriangle, CheckCircle2 } from 'lucide-react';
import { getAQIMetadata } from '../../utils/aqiHelpers.js';

export function HealthTips({ effectiveAqi, alertMessage }) {
  const meta = getAQIMetadata(effectiveAqi);
  const isElevated = effectiveAqi > 100;

  return (
    <div
      role="region"
      aria-label="Household air quality alert"
      className={`flex items-start gap-3 rounded-2xl border p-4 ${meta.surfaceClass}`}
    >
      {isElevated ? (
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      ) : (
        <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      )}
      <div className="space-y-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wide">{meta.riskTag}</span>
          <span className="text-xs font-medium opacity-85">
            Household-Adjusted AQI: {effectiveAqi}
          </span>
        </div>
        <p className="text-sm leading-relaxed">{alertMessage}</p>
      </div>
    </div>
  );
}
