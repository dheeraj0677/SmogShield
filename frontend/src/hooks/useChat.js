import { useCallback, useState } from 'react';
import { sendChatMessage } from '../services/api.js';

const INITIAL_WELCOME = {
  id: 'welcome-msg',
  role: 'assistant',
  content:
    "Hi! I'm **SmogShield**, your urban air quality assistant. Ask me about safe outdoor windows, school commutes, low-cost DIY air filters, or how daily choices reduce your family's smog exposure.",
  recommendations: [],
  impactSummary: '',
  followUpPrompts: [
    'How should I protect my family from winter smog today?',
    'What low-cost DIY indoor air quality hacks work best?',
    'How much impact does switching my commute make today?',
  ],
  aiProvider: 'smogshield',
};

export function useChat(city, userProfile) {
  const [messages, setMessages] = useState([INITIAL_WELCOME]);
  const [sending, setSending] = useState(false);
  const [chatError, setChatError] = useState(null);

  const sendMessage = useCallback(
    async (rawText) => {
      const text = rawText.trim();
      if (!text || sending) return;

      const userMsg = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: text,
      };

      const historyPayload = messages
        .filter((m) => m.id !== 'welcome-msg')
        .slice(-8)
        .map((m) => ({ role: m.role, content: m.content }));

      setMessages((prev) => [...prev, userMsg]);
      setSending(true);
      setChatError(null);

      try {
        const res = await sendChatMessage({
          message: text,
          city,
          userProfile,
          history: historyPayload,
        });

        const assistantMsg = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: res.reply,
          recommendations: res.recommendations || [],
          impactSummary: res.impact_summary || '',
          followUpPrompts: res.follow_up_prompts || [],
          aiProvider: res.ai_provider || 'smogshield',
          disclaimer: res.disclaimer,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        setChatError(err.message || 'Failed to get a response. Please try again.');
      } finally {
        setSending(false);
      }
    },
    [city, messages, sending, userProfile]
  );

  const clearChat = useCallback(() => {
    setMessages([INITIAL_WELCOME]);
    setChatError(null);
  }, []);

  return {
    messages,
    sending,
    chatError,
    sendMessage,
    clearChat,
  };
}
