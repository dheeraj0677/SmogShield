import { CalendarClock, Leaf, Route, Sparkles, Users2 } from 'lucide-react';
import { RevealSection } from '../common/RevealSection.jsx';
import { AlternativesList } from './AlternativesList.jsx';
import { CommunityHub } from './CommunityHub.jsx';
import { DailyRoutine } from './DailyRoutine.jsx';
import { IndoorHacks } from './IndoorHacks.jsx';
import { TransitPlanner } from './TransitPlanner.jsx';

const PLAN_TABS = [
  { id: 'routine', label: 'Daily Routine', icon: CalendarClock },
  { id: 'indoor', label: 'Indoor Air Hacks', icon: Sparkles },
  { id: 'transit', label: 'Clean Commute', icon: Route },
  { id: 'alternatives', label: 'Alternatives', icon: Leaf },
  { id: 'community', label: 'Community & Alerts', icon: Users2 },
];

export function ActionPlansPanel({
  activeTab,
  onSelectTab,
  recommendations,
  aqiSnapshot,
  fallbackCity,
}) {
  if (!recommendations) return null;

  return (
    <RevealSection
      as="section"
      id="action-plans"
      variant="zoom"
      ariaLabel="Personalized action plans"
      className="space-y-4 rounded-3xl border border-slate-200 bg-white/80 p-4 shadow-sm backdrop-blur-sm sm:p-5 dark:border-slate-800 dark:bg-slate-900/70"
    >
      <div
        role="tablist"
        aria-label="Action plan categories"
        className="custom-scrollbar flex gap-2 overflow-x-auto border-b border-slate-200 pb-3 dark:border-slate-800"
      >
        {PLAN_TABS.map((tab) => {
          const Icon = tab.icon;
          const selected = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              type="button"
              id={`tab-${tab.id}`}
              aria-selected={selected}
              aria-controls={`panel-${tab.id}`}
              onClick={() => onSelectTab(tab.id)}
              className={`inline-flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                selected
                  ? 'bg-teal-700 text-white shadow-sm'
                  : 'bg-white text-slate-700 hover:bg-slate-100 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800'
              }`}
            >
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div role="tabpanel" id={`panel-${activeTab}`} aria-labelledby={`tab-${activeTab}`}>
        {activeTab === 'routine' && (
          <DailyRoutine
            schedule={recommendations.schedule}
            routineItems={recommendations.daily_routine}
          />
        )}
        {activeTab === 'indoor' && (
          <IndoorHacks
            hacks={recommendations.indoor_hacks}
            healthProtections={recommendations.health_protections}
            outdoorPm25={aqiSnapshot?.pollutants?.pm25 || 150}
          />
        )}
        {activeTab === 'transit' && (
          <TransitPlanner city={aqiSnapshot?.resolved_city || fallbackCity} />
        )}
        {activeTab === 'alternatives' && (
          <AlternativesList alternatives={recommendations.alternatives} />
        )}
        {activeTab === 'community' && (
          <CommunityHub effectiveAqi={recommendations.effective_aqi} />
        )}
      </div>
    </RevealSection>
  );
}
