import { fireEvent, render, screen } from '@testing-library/react';
import { ShieldCheck } from 'lucide-react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AccessibleIcon } from '../components/common/AccessibleIcon.jsx';
import { ScrollControls } from '../components/common/ScrollControls.jsx';
import {
  calculateRoomCADR,
  fetchAQI,
  fetchAQIByCoordinates,
  fetchAQIByIP,
  fetchCommutePlan,
} from '../services/api.js';

describe('Utility Components & API Client', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders AccessibleIcon with screen-reader text and hidden svg', () => {
    render(<AccessibleIcon icon={ShieldCheck} label="Air protection active" />);
    expect(screen.getByText('Air protection active')).toBeInTheDocument();
  });

  it('toggles ScrollControls back-to-top button on scroll', () => {
    window.scrollTo = vi.fn();
    render(<ScrollControls />);
    Object.defineProperty(window, 'scrollY', { value: 450, configurable: true });
    fireEvent.scroll(window);
    const btn = screen.getByRole('button', { name: /scroll back to top/i });
    fireEvent.click(btn);
    expect(window.scrollTo).toHaveBeenCalled();
  });

  it('covers API client helper functions and error handling', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ aqi: 120 }),
      })
    );

    expect(await fetchAQI('Delhi')).toEqual({ aqi: 120 });
    expect(await fetchAQIByCoordinates(28.6, 77.2)).toEqual({ aqi: 120 });
    expect(await fetchAQIByIP()).toEqual({ aqi: 120 });
    expect(await calculateRoomCADR({ room_area_sqft: 200 })).toEqual({ aqi: 120 });
    expect(await fetchCommutePlan({ city: 'Delhi', distance_km: 5, wear_n95_mask: true })).toEqual({
      aqi: 120,
    });

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'City not found' }),
      })
    );
    await expect(fetchAQI('Unknown')).rejects.toThrow('City not found');
  });
});
