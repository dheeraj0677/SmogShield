# Accessibility Compliance (WCAG 2.1 / 2.2 Level AA) — SmogShield

## Inclusive Design Highlights

1. **Semantic HTML5 Landmarks & Navigation**:
   - Uses `<header>`, `<aside>`, `<main>`, `<section>`, `<article>`, `<footer>`, `role="tablist"`, `role="tab"`, `role="tabpanel"`, and a keyboard-focusable **Skip to main content** anchor (`SkipToContent.jsx`).
2. **Light / Dark Theme & Large-Text Accessibility Modes**:
   - **Light / Dark Toggle (`Header.jsx`, `index.css`)**: Clean Light and Dark Slate themes with WCAG AA+ contrast across all badges, inputs, and charts.
   - **Large Text (`Aa+`) Mode**: Scales base typography (`18px`) and enforces `44px+` interactive target heights.
3. **Screen Reader Twins & Live Regions**:
   - `SmogSparkline.jsx` pairs its native SVG 24-hour diurnal graph with an `.sr-only` hourly text breakdown list.
   - `AQIGauge.jsx` exposes `role="meter"` with `aria-valuemin="0"`, `aria-valuemax="500"`, `aria-valuenow`, and descriptive `aria-valuetext`.
   - `App.jsx` announces AQI updates via `aria-live="polite"`.
4. **Never Color Alone**:
   - Every AQI badge, smog-trapping chip, and daily schedule slot pairs color with explicit text labels (`Good`, `Moderate`, `Hazardous`, `High Risk`).
5. **Multilingual & RTL Support**:
   - `CommunityHub.jsx` provides emergency family advisories in **English**, **Hindi (`हिन्दी`)**, **Urdu (`اردو` with automatic `dir="rtl"`)**, and **Spanish (`Español`)**.
6. **Reduced Motion & Automated Linting**:
   - `index.css` honors `@media (prefers-reduced-motion: reduce)`.
   - `eslint-plugin-jsx-a11y` checks every JSX file with `0` warnings or errors.
