import { useCallback, useState } from 'react';

/**
 * React hook wrapping browser Geolocation API with loading and error state.
 * @returns {object} Geolocation status, error setter/clearer, and requestCoordinates.
 */
export function useGeolocation() {
  const [locating, setLocating] = useState(false);
  const [geoError, setGeoError] = useState(null);

  const clearGeoError = useCallback(() => setGeoError(null), []);

  const requestCoordinates = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        const err = new Error('Geolocation is not supported by your browser.');
        setGeoError(err.message);
        reject(err);
        return;
      }

      setLocating(true);
      setGeoError(null);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocating(false);
          resolve({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });
        },
        (err) => {
          setLocating(false);
          const msg = err.message || 'Unable to access your location.';
          setGeoError(msg);
          reject(new Error(msg));
        },
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
      );
    });
  }, []);

  return { locating, geoError, setGeoError, clearGeoError, requestCoordinates };
}
