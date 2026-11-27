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

export async function fetchAQI(city) {
  return requestJson(`/api/aqi/${encodeURIComponent(city.trim())}`);
}

export async function fetchAQIByCoordinates(lat, lon) {
  return requestJson(
    `/api/aqi/coordinates?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`
  );
}

export async function fetchAQIByIP() {
  return requestJson('/api/aqi/ip-location');
}

export async function fetchRecommendations(userProfile) {
  return requestJson('/api/recommendations', {
    method: 'POST',
    body: JSON.stringify(userProfile),
  });
}

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

export async function calculateRoomCADR(payload) {
  return requestJson('/api/tools/cadr', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchCommutePlan({ city, distance_km, wear_n95_mask }) {
  return requestJson('/api/tools/commute-plan', {
    method: 'POST',
    body: JSON.stringify({ city, distance_km, wear_n95_mask }),
  });
}
