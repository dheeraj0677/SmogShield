import { useEffect, useState } from 'react';
import { ChatWindow } from './components/chat/ChatWindow.jsx';
import { ErrorBoundary } from './components/common/ErrorBoundary.jsx';
import { LoadingSpinner } from './components/common/LoadingSpinner.jsx';
import { RevealSection } from './components/common/RevealSection.jsx';
import { ScrollControls } from './components/common/ScrollControls.jsx';
import { SkipToContent } from './components/common/SkipToContent.jsx';
import { AQIDashboard } from './components/dashboard/AQIDashboard.jsx';
import { AQIScaleBar } from './components/dashboard/AQIScaleBar.jsx';
import { SmogSparkline } from './components/dashboard/SmogSparkline.jsx';
import { VisualGuidesSection } from './components/dashboard/VisualGuidesSection.jsx';
import { Footer } from './components/layout/Footer.jsx';
import { Header } from './components/layout/Header.jsx';
import { HeroStrip } from './components/layout/HeroStrip.jsx';
import { Sidebar } from './components/layout/Sidebar.jsx';
import { ActionPlansPanel } from './components/recommendations/ActionPlansPanel.jsx';
import { ImpactMeter } from './components/recommendations/ImpactMeter.jsx';
import { useAQI } from './hooks/useAQI.js';
import { useChat } from './hooks/useChat.js';
import { useGeolocation } from './hooks/useGeolocation.js';
import { useLocalStorage } from './hooks/useLocalStorage.js';
import { formatAQIAnnouncement } from './utils/accessibility.js';
import { DEFAULT_USER_PROFILE } from './utils/constants.js';

export default function App() {
  const [userProfile, setUserProfile] = useLocalStorage(
    'smogshield_profile_v1',
    DEFAULT_USER_PROFILE
  );
  const [darkMode, setDarkMode] = useLocalStorage('smogshield_dark_mode', false);
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
    loadByIP,
  } = useAQI(userProfile);

  const { locating, geoError, clearGeoError, requestCoordinates } = useGeolocation();
  const { messages, sending, chatError, sendMessage, clearChat } = useChat(
    userProfile.city,
    userProfile
  );

  useEffect(() => {
    document.documentElement.classList.toggle('dark', Boolean(darkMode));
  }, [darkMode]);

  useEffect(() => {
    document.documentElement.classList.toggle('large-text', Boolean(largeText));
  }, [largeText]);

  const handleCityChange = (nextCity) => {
    setUserProfile((prev) => ({ ...prev, city: nextCity }));
  };

  const handleUseGeolocation = async () => {
    try {
      const coords = await requestCoordinates();
      const snapshot = await loadByCoordinates(coords.latitude, coords.longitude, userProfile);
      if (snapshot?.resolved_city) {
        handleCityChange(snapshot.resolved_city);
      }
    } catch {
      // Browser GPS denied, unavailable, or timed out — fall back to IP-based location
      const ipSnapshot = await loadByIP(userProfile);
      if (ipSnapshot?.resolved_city) {
        clearGeoError();
        handleCityChange(ipSnapshot.resolved_city);
      }
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
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode((prev) => !prev)}
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
                <RevealSection variant="right" startVisible className="xl:col-span-7">
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
                </RevealSection>

                <RevealSection variant="left" startVisible delayMs={80} className="xl:col-span-5">
                  <ChatWindow
                    city={aqiSnapshot?.resolved_city || userProfile.city}
                    messages={messages}
                    sending={sending}
                    chatError={chatError}
                    onSendMessage={sendMessage}
                    onClearChat={clearChat}
                  />
                </RevealSection>
              </section>

              {aqiSnapshot && (
                <RevealSection
                  as="section"
                  id="trend-section"
                  variant="up"
                  ariaLabel="Diurnal smog trend and daily impact"
                  className="space-y-4"
                >
                  <AQIScaleBar aqi={aqiSnapshot.aqi} />
                  <SmogSparkline
                    trend={aqiSnapshot.hourly_trend}
                    city={aqiSnapshot.resolved_city}
                  />
                  <ImpactMeter recommendations={recommendations} />
                </RevealSection>
              )}

              <VisualGuidesSection onSelectPlanTab={setActiveTab} />

              <ActionPlansPanel
                activeTab={activeTab}
                onSelectTab={setActiveTab}
                recommendations={recommendations}
                aqiSnapshot={aqiSnapshot}
                fallbackCity={userProfile.city}
              />
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </ErrorBoundary>
  );
}
