import { useRef } from 'react';
import { ArrowRight, ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';
import { RevealSection } from '../common/RevealSection.jsx';

const VISUAL_CARDS = [
  {
    id: 'guide-skyline',
    image: '/images/hero-smog-skyline.jpg',
    alt: 'Illustration of an urban winter skyline protected from smog by a glowing clean-air shield',
    badge: 'Atmospheric Timing',
    title: 'Outsmart Thermal Inversions',
    description:
      'Morning cold air traps particulates at breathing height. Shift outdoor exercise indoors until afternoon mixing clears the air.',
    cta: 'View Daily Routine',
    targetTab: 'routine',
    variant: 'right',
  },
  {
    id: 'guide-indoor',
    image: '/images/indoor-diy-purifier.jpg',
    alt: 'Illustration of a cozy bedroom sanctuary with a sealed window and clean-air HEPA purifier',
    badge: 'Clean Air Sanctuary',
    title: 'Cut Bedroom PM2.5 by 55–70%',
    description:
      'Seal window drafts, switch to wet mopping, and size a True HEPA or DIY box-fan filter to reach the 4.8 ACH sleep benchmark.',
    cta: 'Open CADR & Indoor Hacks',
    targetTab: 'indoor',
    variant: 'up',
  },
  {
    id: 'guide-commute',
    image: '/images/clean-commute-corridor.jpg',
    alt: 'Illustration of an electric metro train and cyclists traveling along a tree-lined park corridor',
    badge: 'Clean Corridor Routing',
    title: 'Save CO₂ & Inhaled Soot Dose',
    description:
      'Swap congested diesel arterials for enclosed electric transit or tree-buffered lanes and inspect exact micrograms saved per trip.',
    cta: 'Plan Clean Commute',
    targetTab: 'transit',
    variant: 'left',
  },
];

export function VisualGuidesSection({ onSelectPlanTab }) {
  const trackRef = useRef(null);

  const scrollTrack = (direction) => {
    if (!trackRef.current) return;
    if (typeof trackRef.current.scrollBy === 'function') {
      trackRef.current.scrollBy({ left: direction * 340, behavior: 'smooth' });
    } else {
      trackRef.current.scrollLeft += direction * 340;
    }
  };

  const handleAction = (tabId) => {
    if (onSelectPlanTab) {
      onSelectPlanTab(tabId);
    }
    const target = document.getElementById('action-plans');
    if (target && typeof target.scrollIntoView === 'function') {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <RevealSection
      as="section"
      id="visual-guides"
      ariaLabel="Visual smog defense playbooks"
      variant="up"
      className="space-y-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="flex items-center gap-2 text-lg font-extrabold tracking-tight text-slate-900 dark:text-white">
            <Sparkles className="h-5 w-5 text-teal-600 dark:text-teal-400" aria-hidden="true" />
            Visual Smog Defense Playbooks
          </h3>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Scroll through illustrated protection strategies and jump straight into each solver
          </p>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => scrollTrack(-1)}
            aria-label="Scroll visual playbooks left"
            className="rounded-xl border border-slate-300 bg-white p-2 text-slate-700 shadow-sm transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={() => scrollTrack(1)}
            aria-label="Scroll visual playbooks right"
            className="rounded-xl border border-slate-300 bg-white p-2 text-slate-700 shadow-sm transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <ChevronRight className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      <div
        ref={trackRef}
        className="custom-scrollbar flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2"
      >
        {VISUAL_CARDS.map((card, index) => (
          <RevealSection
            key={card.id}
            as="article"
            variant={card.variant}
            delayMs={index * 90}
            className="group flex min-w-[290px] flex-1 snap-start flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl sm:min-w-[320px] dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="relative h-44 overflow-hidden bg-slate-100 dark:bg-slate-800">
              <img
                src={card.image}
                alt={card.alt}
                loading="lazy"
                className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
              />
              <div
                className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/75 via-slate-950/20 to-transparent"
                aria-hidden="true"
              />
              <span className="absolute bottom-3 left-3 rounded-full bg-teal-600/95 px-3 py-1 text-[11px] font-bold text-white shadow">
                {card.badge}
              </span>
            </div>

            <div className="flex flex-1 flex-col justify-between p-4">
              <div>
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  {card.title}
                </h4>
                <p className="mt-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                  {card.description}
                </p>
              </div>

              <button
                type="button"
                onClick={() => handleAction(card.targetTab)}
                className="mt-4 inline-flex items-center justify-between rounded-xl bg-teal-50 px-3.5 py-2 text-xs font-bold text-teal-800 transition hover:bg-teal-700 hover:text-white dark:bg-teal-950/60 dark:text-teal-200 dark:hover:bg-teal-700 dark:hover:text-white"
              >
                <span>{card.cta}</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
              </button>
            </div>
          </RevealSection>
        ))}
      </div>
    </RevealSection>
  );
}
