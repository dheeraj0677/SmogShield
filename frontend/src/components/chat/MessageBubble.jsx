import { Bot, Sparkles, User } from 'lucide-react';

/**
 * Render simple inline formatting (**bold** and `code`) safely without dangerouslySetInnerHTML.
 */
function renderFormattedLine(line, lineIndex) {
  const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return (
    <span key={lineIndex}>
      {parts.map((part, idx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={idx} className="font-semibold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        if (part.startsWith('`') && part.endsWith('`')) {
          return (
            <code
              key={idx}
              className="rounded bg-slate-200/80 px-1.5 py-0.5 font-mono text-[11px] dark:bg-slate-700"
            >
              {part.slice(1, -1)}
            </code>
          );
        }
        return part;
      })}
    </span>
  );
}

export function MessageBubble({ message, onFollowUpClick }) {
  const isUser = message.role === 'user';
  const lines = String(message.content || '').split('\n');

  return (
    <article
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
      aria-label={isUser ? 'Your message' : 'SmogShield assistant response'}
    >
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser
            ? 'bg-teal-700 text-white'
            : 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-teal-300'
        }`}
        aria-hidden="true"
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div
        className={`max-w-[88%] space-y-2.5 rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-teal-700 text-white'
            : 'border border-slate-200 bg-slate-50 text-slate-900 dark:border-slate-700 dark:bg-slate-800/80 dark:text-slate-100'
        }`}
      >
        <div className="space-y-1.5">
          {lines.map((line, i) =>
            line.trim() ? (
              <p key={i}>{renderFormattedLine(line, i)}</p>
            ) : (
              <div key={i} className="h-1" />
            )
          )}
        </div>

        {!isUser && message.impactSummary && (
          <div className="rounded-xl border border-teal-300 bg-teal-50 px-3 py-2 text-xs font-medium text-teal-950 dark:border-teal-800 dark:bg-teal-950/50 dark:text-teal-200">
            <span className="inline-flex items-center gap-1 font-bold">
              <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
              Direct Impact:
            </span>{' '}
            {message.impactSummary}
          </div>
        )}

        {!isUser && message.recommendations?.length > 0 && (
          <div className="space-y-2 pt-1">
            {message.recommendations.slice(0, 2).map((rec) => (
              <div
                key={rec.id}
                className="rounded-xl border border-slate-200 bg-white p-2.5 text-xs dark:border-slate-700 dark:bg-slate-900"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {rec.title}
                  </span>
                  <span className="shrink-0 rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                    {rec.impact_metric}
                  </span>
                </div>
                <p className="mt-1 text-slate-600 dark:text-slate-300">{rec.impact}</p>
              </div>
            ))}
          </div>
        )}

        {!isUser && message.followUpPrompts?.length > 0 && onFollowUpClick && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {message.followUpPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => onFollowUpClick(prompt)}
                className="rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-left text-[11px] font-medium text-slate-700 transition hover:border-teal-500 hover:text-teal-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-teal-400"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
