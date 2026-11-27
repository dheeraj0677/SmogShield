import { useCallback, useEffect, useState } from 'react';
import {
  fetchAQIByCoordinates,
  fetchAQIByIP,
  fetchRecommendations,
} from '../services/api.js';

export function useAQI(userProfile) {
  const [aqiSnapshot, setAqiSnapshot] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadForProfile = useCallback(async (profile) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRecommendations(profile);
      setRecommendations(data);
      setAqiSnapshot(data.aqi_snapshot);
    } catch (err) {
      setError(err.message || 'Unable to load air quality data.');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadByCoordinates = useCallback(async (lat, lon, currentProfile) => {
    setLoading(true);
    setError(null);
    try {
      const snapshot = await fetchAQIByCoordinates(lat, lon);
      setAqiSnapshot(snapshot);
      // Sync resolved coordinates query into recommendations if city resolved
      const recData = await fetchRecommendations({
        ...currentProfile,
        city: snapshot.resolved_city || currentProfile.city,
      }).catch(() => null);
      if (recData) {
        setRecommendations(recData);
      }
      return snapshot;
    } catch (err) {
      setError(err.message || 'Unable to fetch air quality for your coordinates.');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const loadByIP = useCallback(async (currentProfile) => {
    setLoading(true);
    setError(null);
    try {
      const snapshot = await fetchAQIByIP();
      setAqiSnapshot(snapshot);
      const recData = await fetchRecommendations({
        ...currentProfile,
        city: snapshot.resolved_city || currentProfile.city,
      }).catch(() => null);
      if (recData) {
        setRecommendations(recData);
      }
      return snapshot;
    } catch (err) {
      setError(err.message || 'Unable to detect your approximate location.');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadForProfile(userProfile);
  }, [loadForProfile, userProfile]);

  return {
    aqiSnapshot,
    recommendations,
    loading,
    error,
    refresh: () => loadForProfile(userProfile),
    loadByCoordinates,
    loadByIP,
  };
}
