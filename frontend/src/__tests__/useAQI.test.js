import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAQI } from '../hooks/useAQI.js';
import * as api from '../services/api.js';
import { DEFAULT_USER_PROFILE } from '../utils/constants.js';

vi.mock('../services/api.js');

describe('useAQI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads recommendations and AQI snapshot for the user profile', async () => {
    api.fetchRecommendations.mockResolvedValue({
      city: 'Delhi',
      effective_aqi: 300,
      aqi_snapshot: { resolved_city: 'Delhi', aqi: 240, category_label: 'Very Unhealthy' },
    });

    const { result } = renderHook(() => useAQI(DEFAULT_USER_PROFILE));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.aqiSnapshot.aqi).toBe(240);
    expect(result.current.error).toBeNull();
  });

  it('captures error state when API call fails', async () => {
    api.fetchRecommendations.mockRejectedValue(new Error('City not found'));

    const { result } = renderHook(() => useAQI(DEFAULT_USER_PROFILE));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toBe('City not found');
  });
});
