import { API_BASE_URL } from '../utils/constants.js';

async function requestJson(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data?.detail || `Request failed (${response.status})`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
}

/**
 * Fetch live AQI snapshot for a named city.
 * @param {string} city - City name to query.
 * @returns {Promise<object>} Normalized AQI snapshot.
 */
export async function fetchAQI(city) {
  return requestJson(`/api/aqi/${encodeURIComponent(city.trim())}`);
}

/**
 * Fetch live AQI snapshot for geographic coordinates.
 * @param {number} lat - Latitude.
 * @param {number} lon - Longitude.
 * @returns {Promise<object>} Normalized AQI snapshot.
 */
export async function fetchAQIByCoordinates(lat, lon) {
  return requestJson(
    `/api/aqi/coordinates?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`
  );
}

/**
 * Fetch live AQI snapshot using IP-based geolocation fallback.
 * @returns {Promise<object>} Normalized AQI snapshot.
 */
export async function fetchAQIByIP() {
  return requestJson('/api/aqi/ip-location');
}

/**
 * Fetch personalized action plans and AQI snapshot for a household profile.
 * @param {object} userProfile - Household profile payload.
 * @returns {Promise<object>} Recommendations response.
 */
export async function fetchRecommendations(userProfile) {
  return requestJson('/api/recommendations', {
    method: 'POST',
    body: JSON.stringify(userProfile),
  });
}

/**
 * Send a prompt to the SmogShield AI Advisor endpoint.
 * @param {object} params - Message, city, userProfile, and history.
 * @returns {Promise<object>} AI reply and follow-up suggestions.
 */
export async function sendChatMessage({ message, city, userProfile, history = [] }) {
  return requestJson('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      city,
      user_profile: userProfile,
      history,
    }),
  });
}

/**
 * Compute indoor purifier ACH and clean-air decay metrics.
 * @param {object} payload - Room dimensions and purifier CADR.
 * @returns {Promise<object>} CADR calculation result.
 */
export async function calculateRoomCADR(payload) {
  return requestJson('/api/tools/cadr', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Compute clean-corridor Dijkstra commute plan and inhaled dose comparison.
 * @param {object} params - City, commute distance, and mask flag.
 * @returns {Promise<object>} Commute dose comparison.
 */
export async function fetchCommutePlan({ city, distance_km, wear_n95_mask }) {
  return requestJson('/api/tools/commute-plan', {
    method: 'POST',
    body: JSON.stringify({ city, distance_km, wear_n95_mask }),
  });
}
