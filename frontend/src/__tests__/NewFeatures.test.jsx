import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ScrollControls } from '../components/common/ScrollControls.jsx';
import { RevealSection } from '../components/common/RevealSection.jsx';
import { AQIScaleBar } from '../components/dashboard/AQIScaleBar.jsx';
import { SmogSparkline } from '../components/dashboard/SmogSparkline.jsx';
import { VisualGuidesSection } from '../components/dashboard/VisualGuidesSection.jsx';
import { Header } from '../components/layout/Header.jsx';
import { HeroStrip } from '../components/layout/HeroStrip.jsx';
import { CADRCalculator } from '../components/recommendations/CADRCalculator.jsx';
import { CommunityHub } from '../components/recommendations/CommunityHub.jsx';
import { TransitPlanner } from '../components/recommendations/TransitPlanner.jsx';
import * as api from '../services/api.js';

vi.mock('../services/api.js');

describe('SmogSparkline & Accessibility Twins', () => {
  it('renders native SVG diurnal chart and paired screen-reader text twin', () => {
    render(
      <SmogSparkline
        city="Delhi"
        trend={[
          { hour: '08:00', aqi: 290, pm25: 190 },
          { hour: '14:00', aqi: 185, pm25: 110 },
          { hour: '22:00', aqi: 310, pm25: 215 },
        ]}
      />
    );

    expect(screen.getByRole('img', { name: /24-hour diurnal AQI trend for Delhi/i })).toBeInTheDocument();
    expect(screen.getByText(/Peak: 22:00 \(AQI 310\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Safest Window: 14:00 \(AQI 185\)/i)).toBeInTheDocument();
    expect(screen.getByText(/At 14:00: AQI 185/i)).toBeInTheDocument();
  });
});

describe('CADRCalculator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('computes room ACH and clean-air decay timeline', async () => {
    api.calculateRoomCADR.mockResolvedValue({
      room_volume_m3: 42.9,
      ach: 5.59,
      recommended_cadr_m3h: 205.9,
      initial_indoor_pm25: 72.0,
      projected_steady_pm25: 5.9,
      minutes_to_safe_air: 17,
      meets_target_ach: true,
      efficiency_note: 'Achieves 5.59 ACH (meets ≥4.8 ACH clean-air sanctuary standard).',
    });

    const user = userEvent.setup();
    render(<CADRCalculator outdoorPm25={160} />);

    await waitFor(() => expect(screen.getByText('5.59 ACH')).toBeInTheDocument());
    expect(screen.getByText('17 min')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Living Room HEPA/i }));
    expect(api.calculateRoomCADR).toHaveBeenCalledTimes(2);
  });
});

describe('TransitPlanner', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays Dijkstra clean corridor and modal comparison table', async () => {
    api.fetchCommutePlan.mockResolvedValue({
      city: 'Delhi',
      ambient_aqi: 250,
      ambient_pm25: 170,
      corridor_analysis: {
        cleanest_route: {
          path: ['Home', 'Metro Concourse', 'Greenbelt Path', 'Work / School'],
          duration_min: 25,
          inhaled_pm25_ug: 28.4,
        },
        standard_arterial: { inhaled_pm25_ug: 88.2 },
        pm25_dose_saved_ug: 59.8,
        exposure_reduction_pct: 68,
        summary: 'Choosing Metro + Greenbelt cuts inhaled PM2.5 by 68%.',
      },
      mode_comparisons: [
        {
          mode: 'public_transit',
          label: 'Electric Metro / AC Bus',
          duration_min: 34,
          inhaled_pm25_ug: 18.2,
          co2_kg: 0.56,
          exposure_vs_peak_pct: 78,
          recommended: true,
        },
      ],
    });

    render(<TransitPlanner city="Delhi" />);

    await waitFor(() => expect(screen.getByText(/-68% PM2.5 Dose/i)).toBeInTheDocument());
    expect(screen.getByText(/Electric Metro \/ AC Bus/i)).toBeInTheDocument();
  });
});

describe('CommunityHub & Multilingual RTL Advisories', () => {
  it('switches across all 4 advisory languages and updates pledge totals', async () => {
    const user = userEvent.setup();
    render(<CommunityHub effectiveAqi={240} />);

    await user.click(screen.getByRole('button', { name: /Hindi/i }));
    const advisorySection = screen.getByLabelText(/Multilingual emergency smog advisory/i);
    expect(advisorySection).toHaveAttribute('dir', 'ltr');
    expect(screen.getByText(/परिवार के लिए स्मॉग आपातकालीन सलाह/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Spanish/i }));
    expect(screen.getByText(/Aviso Familiar de Emergencia por Smog/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Urdu/i }));
    expect(advisorySection).toHaveAttribute('dir', 'rtl');

    await user.click(screen.getByRole('button', { name: /3-Person School & Office Carpool/i }));
    expect(screen.getByText(/4.1 kg CO₂/i)).toBeInTheDocument();
  });

  it('allows clicking preset city chips and submitting custom city search', async () => {
    const user = userEvent.setup();
    const onCityChange = vi.fn();

    render(
      <Header
        city="Delhi"
        onCityChange={onCityChange}
        onUseGeolocation={vi.fn()}
        locating={false}
        aqiSnapshot={{ aqi: 210 }}
        themeMode="light"
        onCycleTheme={vi.fn()}
        largeText={false}
        onToggleLargeText={vi.fn()}
        onToggleSidebar={vi.fn()}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Lahore' }));
    expect(onCityChange).toHaveBeenCalledWith('Lahore');

    const input = screen.getByLabelText(/Enter city name/i);
    await user.clear(input);
    await user.type(input, 'Beijing');
    await user.click(screen.getByRole('button', { name: 'Check' }));
    expect(onCityChange).toHaveBeenCalledWith('Beijing');
  });
});

describe('Header Accessibility Controls', () => {
  it('supports theme cycling and large-text mode toggles', async () => {
    const user = userEvent.setup();
    const onCycleTheme = vi.fn();
    const onToggleLargeText = vi.fn();

    render(
      <Header
        city="Delhi"
        onCityChange={vi.fn()}
        onUseGeolocation={vi.fn()}
        locating={false}
        aqiSnapshot={{ aqi: 210 }}
        themeMode="high-contrast"
        onCycleTheme={onCycleTheme}
        largeText={true}
        onToggleLargeText={onToggleLargeText}
        onToggleSidebar={vi.fn()}
      />
    );

    const themeBtns = screen.getAllByRole('button', { name: /Cycle theme mode/i });
    await user.click(themeBtns[0]);
    expect(onCycleTheme).toHaveBeenCalled();

    const textBtns = screen.getAllByRole('button', { name: /Toggle large readable text/i });
    await user.click(textBtns[0]);
    expect(onToggleLargeText).toHaveBeenCalled();
  });
});

describe('HeroStrip & ScrollControls', () => {
  it('renders hotspot carousel, jump links, and triggers city selection & scrolling', async () => {
    const user = userEvent.setup();
    const onSelectCity = vi.fn();

    render(
      <>
        <ScrollControls />
        <HeroStrip
          city="Delhi"
          aqiSnapshot={{
            resolved_city: 'Delhi',
            aqi: 245,
            pollutants: { pm25: 165 },
            weather: {
              wind_speed_kmh: 5.1,
              smog_trapping_risk: 'high',
              dispersion_note: 'Calm winds trap winter particulates.',
            },
          }}
          onSelectCity={onSelectCity}
        />
      </>
    );

    expect(screen.getByRole('link', { name: /Live Telemetry & AI/i })).toHaveAttribute(
      'href',
      '#overview'
    );
    await user.click(screen.getByRole('button', { name: /Scroll hotspot cities right/i }));
    await user.click(screen.getByRole('button', { name: /Lahore/i }));
    expect(onSelectCity).toHaveBeenCalledWith('Lahore');
  });
});

describe('VisualGuidesSection, AQIScaleBar & RevealSection', () => {
  it('renders EPA spectrum bar, visual playbooks, and switches tabs on CTA click', async () => {
    const user = userEvent.setup();
    const onSelectPlanTab = vi.fn();

    render(
      <RevealSection variant="up">
        <AQIScaleBar aqi={240} />
        <VisualGuidesSection onSelectPlanTab={onSelectPlanTab} />
      </RevealSection>
    );

    expect(screen.getByText(/Current Marker: 240 \/ 500/i)).toBeInTheDocument();
    expect(screen.getByText(/Visual Smog Defense Playbooks/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Scroll visual playbooks right/i }));
    await user.click(screen.getByRole('button', { name: /Plan Clean Commute/i }));
    expect(onSelectPlanTab).toHaveBeenCalledWith('transit');
  });

  it('toggles scroll-in and scroll-out animation classes via IntersectionObserver', async () => {
    let observerCallback = null;
    const originalIO = window.IntersectionObserver;
    window.IntersectionObserver = class {
      constructor(cb) {
        observerCallback = cb;
      }
      observe() {}
      disconnect() {}
    };

    try {
      const { act } = await import('@testing-library/react');
      const { container } = render(
        <RevealSection variant="up">
          <span>Animated Content</span>
        </RevealSection>
      );
      const wrapper = container.firstChild;
      expect(wrapper.className).toContain('opacity-0');

      act(() => observerCallback([{ isIntersecting: true }]));
      expect(wrapper.className).toContain('opacity-100');

      act(() => observerCallback([{ isIntersecting: false }]));
      expect(wrapper.className).toContain('opacity-0');
    } finally {
      window.IntersectionObserver = originalIO;
    }
  });
});
