import { useEffect, useRef } from 'react';
import { MessageSquareText, RotateCcw } from 'lucide-react';
import { QUICK_CHAT_PROMPTS } from '../../utils/constants.js';
import { ChatInput } from './ChatInput.jsx';
import { MessageBubble } from './MessageBubble.jsx';
import { TypingIndicator } from './TypingIndicator.jsx';

export function ChatWindow({
  city,
  messages,
  sending,
  chatError,
  onSendMessage,
  onClearChat,
}) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, sending]);

  return (
    <section
      aria-label="SmogShield GenAI Assistant Chat"
      className="flex h-[580px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-teal-700/5 to-transparent px-4 py-3 dark:border-slate-800 dark:from-teal-500/10">
        <div className="flex items-center gap-2">
          <MessageSquareText className="h-5 w-5 text-teal-600 dark:text-teal-400" aria-hidden="true" />
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">
              SmogShield AI Advisor
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Grounded in live {city} AQI &amp; household context
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClearChat}
          aria-label="Reset conversation"
          className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
          Reset
        </button>
      </div>

      <div className="custom-scrollbar flex gap-1.5 overflow-x-auto border-b border-slate-100 bg-slate-50/80 px-4 py-2 dark:border-slate-800 dark:bg-slate-950/40">
        {QUICK_CHAT_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            disabled={sending}
            onClick={() => onSendMessage(prompt)}
            className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-700 transition hover:border-teal-500 hover:text-teal-700 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
          >
            {prompt}
          </button>
        ))}
      </div>

      <div
        ref={scrollRef}
        className="custom-scrollbar flex-1 space-y-4 overflow-y-auto p-4"
        aria-live="polite"
      >
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onFollowUpClick={(prompt) => onSendMessage(prompt)}
          />
        ))}
        {sending && <TypingIndicator />}
        {chatError && (
          <div
            role="alert"
            className="rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-xs text-red-900 dark:border-red-800 dark:bg-red-950/50 dark:text-red-200"
          >
            {chatError}
          </div>
        )}
      </div>

      <ChatInput onSend={onSendMessage} disabled={sending} />
    </section>
  );
}
