/**
 * Map numeric US EPA AQI values to accessible colors, badges, and status text.
 */
export function getAQIMetadata(aqi = 0) {
  const value = Math.max(0, Math.min(500, Number(aqi) || 0));

  if (value <= 50) {
    return {
      category: 'good',
      label: 'Good',
      badgeClass: 'bg-emerald-700 text-white',
      ringColor: '#15803d',
      surfaceClass:
        'bg-emerald-50 border-emerald-200 text-emerald-950 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-100',
      riskTag: 'Low Risk',
    };
  }
  if (value <= 100) {
    return {
      category: 'moderate',
      label: 'Moderate',
      badgeClass: 'bg-amber-400 text-slate-950',
      ringColor: '#ca8a04',
      surfaceClass:
        'bg-amber-50 border-amber-300 text-amber-950 dark:bg-amber-950/40 dark:border-amber-700 dark:text-amber-100',
      riskTag: 'Moderate Risk',
    };
  }
  if (value <= 150) {
    return {
      category: 'unhealthy_sensitive',
      label: 'Unhealthy (Sensitive)',
      badgeClass: 'bg-orange-600 text-white',
      ringColor: '#ea580c',
      surfaceClass:
        'bg-orange-50 border-orange-300 text-orange-950 dark:bg-orange-950/40 dark:border-orange-700 dark:text-orange-100',
      riskTag: 'Sensitive Alert',
    };
  }
  if (value <= 200) {
    return {
      category: 'unhealthy',
      label: 'Unhealthy',
      badgeClass: 'bg-red-600 text-white',
      ringColor: '#dc2626',
      surfaceClass:
        'bg-red-50 border-red-300 text-red-950 dark:bg-red-950/40 dark:border-red-700 dark:text-red-100',
      riskTag: 'High Risk',
    };
  }
  if (value <= 300) {
    return {
      category: 'very_unhealthy',
      label: 'Very Unhealthy',
      badgeClass: 'bg-purple-700 text-white',
      ringColor: '#7e22ce',
      surfaceClass:
        'bg-purple-50 border-purple-300 text-purple-950 dark:bg-purple-950/40 dark:border-purple-700 dark:text-purple-100',
      riskTag: 'Very High Risk',
    };
  }
  return {
    category: 'hazardous',
    label: 'Hazardous',
    badgeClass: 'bg-rose-900 text-white',
    ringColor: '#881337',
    surfaceClass:
      'bg-rose-50 border-rose-300 text-rose-950 dark:bg-rose-950/50 dark:border-rose-800 dark:text-rose-100',
    riskTag: 'Emergency',
  };
}

export const POLLUTANT_LABELS = {
  pm25: { label: 'PM2.5', unit: 'µg/m³', limit: 35.4, detail: 'Fine breathable soot' },
  pm10: { label: 'PM10', unit: 'µg/m³', limit: 154, detail: 'Coarse dust & smoke' },
  o3: { label: 'O₃', unit: 'µg/m³', limit: 137, detail: 'Ground-level ozone' },
  no2: { label: 'NO₂', unit: 'µg/m³', limit: 188, detail: 'Traffic exhaust gas' },
  so2: { label: 'SO₂', unit: 'µg/m³', limit: 196, detail: 'Combustion sulfur' },
  co: { label: 'CO', unit: 'mg/m³', limit: 10.8, detail: 'Carbon monoxide' },
};
