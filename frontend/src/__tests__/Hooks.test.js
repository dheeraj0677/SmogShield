import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { useAQI } from '../hooks/useAQI.js';
import { useChat } from '../hooks/useChat.js';
import { useGeolocation } from '../hooks/useGeolocation.js';
import { useLocalStorage } from '../hooks/useLocalStorage.js';
import * as api from '../services/api.js';

describe('Frontend Hooks Coverage', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('useGeolocation handles success, error, and unsupported browser', async () => {
    const origGeo = navigator.geolocation;
    Object.defineProperty(navigator, 'geolocation', {
      configurable: true,
      value: {
        getCurrentPosition: (ok) => ok({ coords: { latitude: 17.38, longitude: 78.48 } }),
      },
    });
    const { result } = renderHook(() => useGeolocation());
    let coords;
    await act(async () => {
      coords = await result.current.requestCoordinates();
    });
    expect(coords).toEqual({ latitude: 17.38, longitude: 78.48 });

    Object.defineProperty(navigator, 'geolocation', {
      configurable: true,
      value: {
        getCurrentPosition: (_ok, err) => err({ message: 'Timeout expired' }),
      },
    });
    await act(async () => {
      await expect(result.current.requestCoordinates()).rejects.toThrow('Timeout expired');
    });
    expect(result.current.geoError).toBe('Timeout expired');

    act(() => result.current.clearGeoError());
    expect(result.current.geoError).toBeNull();

    Object.defineProperty(navigator, 'geolocation', { configurable: true, value: undefined });
    await act(async () => {
      await expect(result.current.requestCoordinates()).rejects.toThrow('not supported');
    });
    Object.defineProperty(navigator, 'geolocation', { configurable: true, value: origGeo });
  });

  it('useChat sends messages, handles errors, and resets', async () => {
    vi.spyOn(api, 'sendChatMessage').mockResolvedValueOnce({
      reply: 'Use an N95 mask.',
      recommendations: [],
      impact_summary: '40% less PM2.5',
      follow_up_prompts: ['Next tip?'],
      ai_provider: 'openrouter',
    });

    const { result } = renderHook(() => useChat('Delhi', { city: 'Delhi' }));
    await act(async () => {
      await result.current.sendMessage('Should I wear a mask?');
    });
    expect(result.current.messages).toHaveLength(3);
    expect(result.current.messages[2].content).toBe('Use an N95 mask.');

    vi.spyOn(api, 'sendChatMessage').mockRejectedValueOnce(new Error('Network down'));
    await act(async () => {
      await result.current.sendMessage('Retry?');
    });
    expect(result.current.chatError).toBe('Network down');

    act(() => result.current.clearChat());
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.chatError).toBeNull();
  });

  it('useLocalStorage falls back gracefully on corrupted JSON', () => {
    window.localStorage.setItem('bad_key', '{not-json');
    const { result } = renderHook(() => useLocalStorage('bad_key', { ok: true }));
    expect(result.current[0]).toEqual({ ok: true });
    act(() => result.current[1]({ ok: false }));
    expect(result.current[0]).toEqual({ ok: false });
  });

  it('useAQI supports loadByCoordinates, loadByIP, and error fallback', async () => {
    vi.spyOn(api, 'fetchRecommendations').mockResolvedValue({
      aqi_snapshot: { resolved_city: 'Delhi', aqi: 180 },
      daily_schedule: [],
    });
    vi.spyOn(api, 'fetchAQIByCoordinates').mockResolvedValue({
      resolved_city: 'Hyderabad',
      aqi: 95,
    });
    vi.spyOn(api, 'fetchAQIByIP').mockResolvedValue({
      resolved_city: 'Bengaluru',
      aqi: 62,
    });

    const profile = { city: 'Delhi' };
    const { result } = renderHook(() => useAQI(profile));
    await act(async () => {});

    await act(async () => {
      const snap = await result.current.loadByCoordinates(17.38, 78.48, profile);
      expect(snap.resolved_city).toBe('Hyderabad');
    });

    await act(async () => {
      const ipSnap = await result.current.loadByIP(profile);
      expect(ipSnap.resolved_city).toBe('Bengaluru');
    });
  });
});
