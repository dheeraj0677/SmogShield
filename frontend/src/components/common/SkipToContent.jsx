export function SkipToContent({ targetId = 'main-content' }) {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only-focusable fixed left-4 top-4 z-50 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white shadow-lg"
    >
      Skip to main content
    </a>
  );
}
