import { useEffect, useRef, useState } from 'react';

const VARIANT_HIDDEN = {
  up: 'opacity-0 translate-y-7 scale-[0.985]',
  down: 'opacity-0 -translate-y-7 scale-[0.985]',
  left: 'opacity-0 translate-x-7',
  right: 'opacity-0 -translate-x-7',
  zoom: 'opacity-0 scale-95',
};

const VARIANT_VISIBLE = 'opacity-100 translate-y-0 translate-x-0 scale-100';

export function RevealSection({
  children,
  variant = 'up',
  delayMs = 0,
  className = '',
  id,
  as = 'div',
  ariaLabel,
  startVisible = false,
}) {
  const Tag = as;
  const ref = useRef(null);
  const [visible, setVisible] = useState(
    () => startVisible || typeof window === 'undefined' || typeof IntersectionObserver === 'undefined'
  );

  useEffect(() => {
    if (startVisible || typeof IntersectionObserver === 'undefined') {
      setVisible(true);
      return undefined;
    }

    const el = ref.current;
    if (!el) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          setVisible(entry.isIntersecting);
        }
      },
      {
        threshold: 0.08,
        rootMargin: '0px 0px -30px 0px',
      }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [startVisible]);

  const hiddenClasses = VARIANT_HIDDEN[variant] || VARIANT_HIDDEN.up;

  return (
    <Tag
      ref={ref}
      id={id}
      aria-label={ariaLabel}
      style={delayMs ? { transitionDelay: `${delayMs}ms` } : undefined}
      className={`transform-gpu transition-all duration-700 ease-out will-change-transform ${
        visible ? VARIANT_VISIBLE : hiddenClasses
      } ${className}`}
    >
      {children}
    </Tag>
  );
}
