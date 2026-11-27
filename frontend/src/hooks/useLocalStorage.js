import { useEffect, useState } from 'react';

/**
 * React hook persisting state in browser localStorage with safe JSON fallback.
 * @param {string} key - Storage key name.
 * @param {*} initialValue - Fallback value when storage is empty or unavailable.
 * @returns {Array} Tuple of [storedValue, setStoredValue].
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(storedValue));
    } catch {
      // Ignore storage quota or private-mode errors
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue];
}
