import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { RevealSection } from '../components/common/RevealSection.jsx';
import { ScrollControls } from '../components/common/ScrollControls.jsx';
import { AQIScaleBar } from '../components/dashboard/AQIScaleBar.jsx';
import { VisualGuidesSection } from '../components/dashboard/VisualGuidesSection.jsx';
import { Header } from '../components/layout/Header.jsx';
import { HeroStrip } from '../components/layout/HeroStrip.jsx';

describe('Header Accessibility Controls', () => {
  it('supports dark/light mode and large-text mode toggles', async () => {
    const user = userEvent.setup();
    const onToggleDarkMode = vi.fn();
    const onToggleLargeText = vi.fn();

    render(
      <Header
        city="Delhi"
        onCityChange={vi.fn()}
        onUseGeolocation={vi.fn()}
        locating={false}
        aqiSnapshot={{ aqi: 210 }}
        darkMode={true}
        onToggleDarkMode={onToggleDarkMode}
        largeText={true}
        onToggleLargeText={onToggleLargeText}
        onToggleSidebar={vi.fn()}
      />
    );

    const themeBtns = screen.getAllByRole('button', { name: /Switch to light mode/i });
    await user.click(themeBtns[0]);
    expect(onToggleDarkMode).toHaveBeenCalled();

    const textBtns = screen.getAllByRole('button', { name: /Aa\+ — Toggle large readable text/i });
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
