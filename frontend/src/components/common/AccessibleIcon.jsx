export function AccessibleIcon({ icon: Icon, label, className = 'h-4 w-4' }) {
  if (!Icon) return null;
  if (label) {
    return (
      <span className="inline-flex items-center">
        <Icon className={className} aria-hidden="true" />
        <span className="sr-only">{label}</span>
      </span>
    );
  }
  return <Icon className={className} aria-hidden="true" />;
}
