import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AQIDashboard } from '../components/dashboard/AQIDashboard.jsx';

const SAMPLE_SNAPSHOT = {
  city: 'Delhi',
  resolved_city: 'Delhi',
  country: 'India',
  aqi: 285,
  category: 'very_unhealthy',
  category_label: 'Very Unhealthy',
  dominant_pollutant: 'pm25',
  data_source: 'open-meteo',
  cached: false,
  pollutants: {
    pm25: 178,
    pm10: 265,
    o3: 42,
    no2: 68,
    so2: 18,
    co: 2.4,
  },
  weather: {
    temperature_c: 14.5,
    humidity_pct: 74,
    wind_speed_kmh: 5.2,
    condition: 'Dense Winter Haze',
    smog_trapping_risk: 'high',
    dispersion_note: 'Stagnant winds trap pollutants near ground level.',
  },
};

const SAMPLE_RECS = {
  effective_aqi: 345,
  alert_message:
    'Live AQI is 285 (Very Unhealthy), effective risk AQI 345 for your household.',
};

describe('AQIDashboard', () => {
  it('renders accessible AQI meter, pollutant cards, and sensitivity alert', () => {
    const onRefresh = vi.fn();
    render(
      <AQIDashboard
        snapshot={SAMPLE_SNAPSHOT}
        recommendations={SAMPLE_RECS}
        loading={false}
        onRefresh={onRefresh}
      />
    );

    expect(screen.getByText(/Delhi, India/i)).toBeInTheDocument();
    const meter = screen.getByRole('meter', { name: /Air Quality Index for Delhi/i });
    expect(meter).toHaveAttribute('aria-valuenow', '285');
    expect(screen.getByText('Very Unhealthy')).toBeInTheDocument();
    expect(screen.getByText(/Household-Adjusted AQI: 345/i)).toBeInTheDocument();
    expect(screen.getByText(/PM2.5/i)).toBeInTheDocument();
    expect(screen.getByText(/high trapping risk/i)).toBeInTheDocument();
  });

  it('triggers refresh callback and renders low-risk state without warnings', async () => {
    const { default: userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();
    const onRefresh = vi.fn();

    render(
      <AQIDashboard
        snapshot={{
          ...SAMPLE_SNAPSHOT,
          resolved_city: 'London',
          country: 'United Kingdom',
          aqi: 28,
          category: 'good',
          category_label: 'Good',
          cached: true,
          weather: {
            ...SAMPLE_SNAPSHOT.weather,
            smog_trapping_risk: 'low',
            dispersion_note: 'Breezy dispersion.',
          },
        }}
        recommendations={{ effective_aqi: 28, alert_message: 'Clean air today.' }}
        loading={false}
        onRefresh={onRefresh}
      />
    );

    expect(screen.getByText(/low trapping risk/i)).toBeInTheDocument();
    expect(screen.getByText(/\(cached\)/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Refresh Live AQI/i }));
    expect(onRefresh).toHaveBeenCalledTimes(1);
  });
});
