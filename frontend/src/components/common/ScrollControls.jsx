import { useEffect, useState } from 'react';
import { ArrowUp } from 'lucide-react';

export function ScrollControls() {
  const [progress, setProgress] = useState(0);
  const [showTop, setShowTop] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight =
        document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const pct = docHeight > 0 ? Math.min(100, Math.round((scrollTop / docHeight) * 100)) : 0;
      setProgress(pct);
      setShowTop(scrollTop > 280);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <div
        aria-hidden="true"
        className="fixed left-0 top-0 z-50 h-1 w-full bg-transparent"
      >
        <div
          className="h-full bg-gradient-to-r from-teal-500 via-emerald-400 to-sky-500 transition-[width] duration-150"
          style={{ width: `${progress}%` }}
        />
      </div>

      {showTop && (
        <button
          type="button"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          aria-label="Scroll back to top"
          className="fixed bottom-5 right-5 z-40 inline-flex items-center gap-1.5 rounded-full bg-teal-700 px-3.5 py-2.5 text-xs font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-teal-800"
        >
          <ArrowUp className="h-4 w-4" aria-hidden="true" />
          <span>Top</span>
        </button>
      )}
    </>
  );
}
