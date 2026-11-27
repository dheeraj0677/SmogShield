import { useEffect, useState } from 'react';
import { CalendarClock, Leaf, Route, Sparkles, Users2 } from 'lucide-react';
import { ChatWindow } from './components/chat/ChatWindow.jsx';
import { ErrorBoundary } from './components/common/ErrorBoundary.jsx';
import { LoadingSpinner } from './components/common/LoadingSpinner.jsx';
import { ScrollControls } from './components/common/ScrollControls.jsx';
import { SkipToContent } from './components/common/SkipToContent.jsx';
import { AQIDashboard } from './components/dashboard/AQIDashboard.jsx';
import { SmogSparkline } from './components/dashboard/SmogSparkline.jsx';
import { Footer } from './components/layout/Footer.jsx';
import { Header } from './components/layout/Header.jsx';
import { HeroStrip } from './components/layout/HeroStrip.jsx';
import { Sidebar } from './components/layout/Sidebar.jsx';
import { AlternativesList } from './components/recommendations/AlternativesList.jsx';
import { CommunityHub } from './components/recommendations/CommunityHub.jsx';
import { DailyRoutine } from './components/recommendations/DailyRoutine.jsx';
import { ImpactMeter } from './components/recommendations/ImpactMeter.jsx';
import { IndoorHacks } from './components/recommendations/IndoorHacks.jsx';
import { TransitPlanner } from './components/recommendations/TransitPlanner.jsx';
import { useAQI } from './hooks/useAQI.js';
import { useChat } from './hooks/useChat.js';
import { useGeolocation } from './hooks/useGeolocation.js';
import { useLocalStorage } from './hooks/useLocalStorage.js';
import { formatAQIAnnouncement } from './utils/accessibility.js';
import { DEFAULT_USER_PROFILE } from './utils/constants.js';

const PLAN_TABS = [
  { id: 'routine', label: 'Daily Routine', icon: CalendarClock },
  { id: 'indoor', label: 'Indoor Air Hacks', icon: Sparkles },
  { id: 'transit', label: 'Clean Commute', icon: Route },
  { id: 'alternatives', label: 'Alternatives', icon: Leaf },
  { id: 'community', label: 'Community & Alerts', icon: Users2 },
];

const THEME_CYCLE = ['light', 'dark', 'high-contrast'];

export default function App() {
  const [userProfile, setUserProfile] = useLocalStorage(
    'smogshield_profile_v1',
    DEFAULT_USER_PROFILE
  );
  const [themeMode, setThemeMode] = useLocalStorage('smogshield_theme_mode', 'light');
  const [largeText, setLargeText] = useLocalStorage('smogshield_large_text', false);
  const [activeTab, setActiveTab] = useState('routine');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const {
    aqiSnapshot,
    recommendations,
    loading,
    error,
    refresh,
    loadByCoordinates,
  } = useAQI(userProfile);

  const { locating, geoError, requestCoordinates } = useGeolocation();
  const { messages, sending, chatError, sendMessage, clearChat } = useChat(
    userProfile.city,
    userProfile
  );

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle('dark', themeMode === 'dark' || themeMode === 'high-contrast');
    root.classList.toggle('high-contrast', themeMode === 'high-contrast');
  }, [themeMode]);

  useEffect(() => {
    document.documentElement.classList.toggle('large-text', Boolean(largeText));
  }, [largeText]);

  const handleCycleTheme = () => {
    setThemeMode((prev) => {
      const idx = THEME_CYCLE.indexOf(prev);
      return THEME_CYCLE[(idx + 1) % THEME_CYCLE.length];
    });
  };

  const handleCityChange = (nextCity) => {
    setUserProfile((prev) => ({ ...prev, city: nextCity }));
  };

  const handleUseGeolocation = async () => {
    try {
      const coords = await requestCoordinates();
      await loadByCoordinates(coords.latitude, coords.longitude, userProfile);
    } catch {
      // Error surfaced via geoError banner
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        <ScrollControls />
        <SkipToContent targetId="main-content" />

        <div className="sr-only" aria-live="polite">
          {formatAQIAnnouncement(aqiSnapshot)}
        </div>

        <Header
          city={userProfile.city}
          onCityChange={handleCityChange}
          onUseGeolocation={handleUseGeolocation}
          locating={locating}
          aqiSnapshot={aqiSnapshot}
          themeMode={themeMode}
          onCycleTheme={handleCycleTheme}
          largeText={largeText}
          onToggleLargeText={() => setLargeText((prev) => !prev)}
          onToggleSidebar={() => setSidebarOpen(true)}
        />

        <main id="main-content" className="mx-auto max-w-7xl space-y-6 px-4 py-6 sm:px-6">
          <HeroStrip
            city={userProfile.city}
            aqiSnapshot={aqiSnapshot}
            onSelectCity={handleCityChange}
          />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            <div className="lg:col-span-3">
              <Sidebar
                profile={userProfile}
                onChangeProfile={setUserProfile}
                openMobile={sidebarOpen}
                onCloseMobile={() => setSidebarOpen(false)}
              />
            </div>

            <div className="space-y-6 lg:col-span-9">
              {geoError && (
                <div
                  role="alert"
                  className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-2.5 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200"
                >
                  Location lookup failed: {geoError}
                </div>
              )}

              {error && (
                <div
                  role="alert"
                  className="rounded-2xl border border-red-300 bg-red-50 p-4 text-sm text-red-900 dark:border-red-800 dark:bg-red-950/50 dark:text-red-200"
                >
                  <p className="font-semibold">Unable to fetch AQI for &quot;{userProfile.city}&quot;</p>
                  <p className="mt-1 text-xs">{error}</p>
                </div>
              )}

              <section id="overview" className="grid grid-cols-1 gap-6 xl:grid-cols-12">
                <div className="xl:col-span-7">
                  {loading && !aqiSnapshot ? (
                    <LoadingSpinner label={`Fetching real-time AQI for ${userProfile.city}...`} />
                  ) : (
                    <AQIDashboard
                      snapshot={aqiSnapshot}
                      recommendations={recommendations}
                      loading={loading}
                      onRefresh={refresh}
                    />
                  )}
                </div>

                <div className="xl:col-span-5">
                  <ChatWindow
                    city={aqiSnapshot?.resolved_city || userProfile.city}
                    messages={messages}
                    sending={sending}
                    chatError={chatError}
                    onSendMessage={sendMessage}
                    onClearChat={clearChat}
                  />
                </div>
              </section>

              {aqiSnapshot && (
                <section id="trend-section" aria-label="Diurnal smog trend and daily impact" className="space-y-4">
                  <SmogSparkline
                    trend={aqiSnapshot.hourly_trend}
                    city={aqiSnapshot.resolved_city}
                  />
                  <ImpactMeter recommendations={recommendations} />
                </section>
              )}

              {recommendations && (
                <section
                  id="action-plans"
                  aria-label="Personalized action plans"
                  className="space-y-4 rounded-3xl border border-slate-200 bg-white/70 p-4 shadow-sm sm:p-5 dark:border-slate-800 dark:bg-slate-900/60"
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
                          onClick={() => setActiveTab(tab.id)}
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

                  <div
                    role="tabpanel"
                    id={`panel-${activeTab}`}
                    aria-labelledby={`tab-${activeTab}`}
                  >
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
                      <TransitPlanner city={aqiSnapshot?.resolved_city || userProfile.city} />
                    )}
                    {activeTab === 'alternatives' && (
                      <AlternativesList alternatives={recommendations.alternatives} />
                    )}
                    {activeTab === 'community' && (
                      <CommunityHub effectiveAqi={recommendations.effective_aqi} />
                    )}
                  </div>
                </section>
              )}
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </ErrorBoundary>
  );
}
