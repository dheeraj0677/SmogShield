import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ErrorBoundary } from '../components/common/ErrorBoundary.jsx';
import { Footer } from '../components/layout/Footer.jsx';
import { Sidebar } from '../components/layout/Sidebar.jsx';
import { AlternativesList } from '../components/recommendations/AlternativesList.jsx';
import { DailyRoutine } from '../components/recommendations/DailyRoutine.jsx';
import { ImpactMeter } from '../components/recommendations/ImpactMeter.jsx';
import { DEFAULT_USER_PROFILE } from '../utils/constants.js';

describe('Sidebar & Household Context', () => {
  it('toggles health sensitivity and purifier options', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(
      <Sidebar
        profile={DEFAULT_USER_PROFILE}
        onChangeProfile={onChange}
        openMobile={false}
        onCloseMobile={vi.fn()}
      />
    );

    await user.click(screen.getByRole('button', { name: 'COPD' }));
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ health_conditions: ['asthma', 'copd'] })
    );

    await user.click(screen.getByLabelText(/Already own a HEPA purifier/i));
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ has_air_purifier: true })
    );
  });
});

describe('Recommendations Views & ImpactMeter', () => {
  it('renders daily schedule slots, alternatives, and quantified impact metrics', () => {
    const recSummary = {
      personalization_summary: 'Location: Delhi (AQI 260) | Household: 3 member(s)',
      estimated_exposure_reduction_pct: 72,
      total_potential_co2_saved_kg: 5.4,
    };

    render(
      <>
        <ImpactMeter recommendations={recSummary} />
        <DailyRoutine
          schedule={[
            {
              time_window: '6:00 AM – 9:30 AM',
              activity: 'Morning Routine',
              recommended_action: 'Exercise indoors.',
              aqi_risk: 'severe',
              rationale: 'Cold inversion traps PM2.5.',
              impact: 'Cuts morning dose by 65%.',
            },
          ]}
          routineItems={[
            {
              id: 'r1',
              title: 'Shift workouts indoors',
              impact_metric: '-65% PM2.5 dose',
              description: 'Avoid morning haze.',
              impact: 'Protects lungs.',
            },
          ]}
        />
        <AlternativesList
          alternatives={[
            {
              id: 'a1',
              title: 'Switch to Electric Metro',
              co2_saved_kg: 2.3,
              description: 'Avoids solo tailpipe exhaust.',
              impact_metric: '2.3 kg CO2 saved',
              impact: 'Cuts exposure by 40%.',
            },
          ]}
        />
        <Footer />
      </>
    );

    expect(screen.getByText('-72%')).toBeInTheDocument();
    expect(screen.getByText('5.4 kg')).toBeInTheDocument();
    expect(screen.getByText('6:00 AM – 9:30 AM')).toBeInTheDocument();
    expect(screen.getByText('Switch to Electric Metro')).toBeInTheDocument();
    expect(screen.getByText(/Challenge 6: Urban Air Quality Assistant/i)).toBeInTheDocument();
  });
});

describe('ErrorBoundary', () => {
  it('catches rendering errors cleanly in ErrorBoundary', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const Broken = () => {
      throw new Error('Test render failure');
    };

    render(
      <ErrorBoundary>
        <Broken />
      </ErrorBoundary>
    );

    expect(screen.getByRole('alert')).toHaveTextContent('Test render failure');
    spy.mockRestore();
  });
});
