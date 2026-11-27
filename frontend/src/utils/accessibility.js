/**
 * Announce live status changes politely to assistive screen readers.
 */
export function formatAQIAnnouncement(snapshot) {
  if (!snapshot) return '';
  return `Air quality for ${snapshot.resolved_city} updated. AQI is ${snapshot.aqi}, categorized as ${snapshot.category_label}.`;
}

export function sanitizeDisplayCity(value = '') {
  return String(value).replace(/[<>]/g, '').trim().slice(0, 80);
}
