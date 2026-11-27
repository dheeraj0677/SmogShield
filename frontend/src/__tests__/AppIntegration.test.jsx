import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../App.jsx';
import * as api from '../services/api.js';

vi.mock('../services/api.js');

describe('App Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('loads App dashboard and switches across all 5 action tabs', async () => {
    api.fetchRecommendations.mockResolvedValue({
      city: 'Delhi',
      effective_aqi: 295,
      alert_message: 'High risk in Delhi.',
      personalization_summary: 'Location: Delhi (AQI 235)',
      estimated_exposure_reduction_pct: 68,
      total_potential_co2_saved_kg: 4.5,
      daily_routine: [],
      indoor_hacks: [
        {
          id: 'h1',
          title: 'DIY Corsi-Rosenthal Filter',
          impact_metric: '-55% indoor PM2.5',
          cost: 'low',
          difficulty: 'moderate',
          best_time: 'Overnight',
          description: 'Box fan with MERV-13 filter.',
          impact: 'Lowers indoor particulates.',
        },
      ],
      health_protections: [],
      alternatives: [
        {
          id: 'a1',
          title: 'Zero-Burn Habits',
          co2_saved_kg: 1.8,
          description: 'Compost dry leaves.',
          impact_metric: '1.8 kg CO2 saved',
          impact: 'Prevents street smoke.',
        },
      ],
      schedule: [
        {
          time_window: '12:30 PM – 3:30 PM',
          activity: 'Midday Reset',
          recommended_action: 'Run purifier.',
          aqi_risk: 'high',
          rationale: 'Light winds.',
          impact: 'Cleaner indoor air.',
        },
      ],
      aqi_snapshot: {
        city: 'Delhi',
        resolved_city: 'Delhi',
        country: 'India',
        aqi: 235,
        category: 'very_unhealthy',
        category_label: 'Very Unhealthy',
        dominant_pollutant: 'pm25',
        data_source: 'open-meteo',
        cached: false,
        pollutants: { pm25: 155, pm10: 210, o3: 45, no2: 60, so2: 14, co: 1.8 },
        weather: {
          temperature_c: 15,
          humidity_pct: 72,
          wind_speed_kmh: 5.5,
          condition: 'Haze',
          smog_trapping_risk: 'high',
          dispersion_note: 'Calm winds trap soot.',
        },
        hourly_trend: [
          { hour: '08:00', aqi: 260, pm25: 170 },
          { hour: '14:00', aqi: 180, pm25: 105 },
        ],
      },
    });
    api.calculateRoomCADR.mockResolvedValue({
      room_volume_m3: 40,
      ach: 6.0,
      recommended_cadr_m3h: 192,
      initial_indoor_pm25: 68,
      projected_steady_pm25: 5,
      minutes_to_safe_air: 15,
      meets_target_ach: true,
      efficiency_note: 'Meets 4.8 ACH target.',
    });
    api.fetchCommutePlan.mockResolvedValue({
      city: 'Delhi',
      ambient_aqi: 235,
      ambient_pm25: 155,
      corridor_analysis: {
        cleanest_route: {
          path: ['Home', 'Metro Concourse', 'Greenbelt Path', 'Work / School'],
          duration_min: 24,
          inhaled_pm25_ug: 25,
        },
        standard_arterial: { inhaled_pm25_ug: 80 },
        pm25_dose_saved_ug: 55,
        exposure_reduction_pct: 69,
        summary: 'Clean path cuts dose by 69%.',
      },
      mode_comparisons: [],
    });

    const user = userEvent.setup();
    render(<App />);

    await waitFor(() => expect(screen.getByText('24-Hour Diurnal Smog Cycle')).toBeInTheDocument());

    await user.click(screen.getByRole('tab', { name: 'Indoor Air Hacks' }));
    expect(screen.getByText('DIY Corsi-Rosenthal Filter')).toBeInTheDocument();

    await user.click(screen.getByRole('tab', { name: 'Clean Commute' }));
    await waitFor(() => expect(screen.getByText(/Recommended Clean Path/i)).toBeInTheDocument());

    await user.click(screen.getByRole('tab', { name: 'Alternatives' }));
    expect(screen.getByText('Zero-Burn Habits')).toBeInTheDocument();

    await user.click(screen.getByRole('tab', { name: 'Community & Alerts' }));
    expect(screen.getByText('Neighborhood Clean-Air Pledges')).toBeInTheDocument();
  });
});
