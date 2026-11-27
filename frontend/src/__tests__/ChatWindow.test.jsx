import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ChatWindow } from '../components/chat/ChatWindow.jsx';

describe('ChatWindow', () => {
  it('renders messages and submits user prompt via form', async () => {
    const user = userEvent.setup();
    const onSendMessage = vi.fn();
    const onClearChat = vi.fn();

    render(
      <ChatWindow
        city="Delhi"
        messages={[
          {
            id: '1',
            role: 'assistant',
            content: 'Live AQI is **285**. Stay indoors.',
            impactSummary: 'Cuts PM2.5 exposure by 65%.',
            recommendations: [],
            followUpPrompts: [],
          },
        ]}
        sending={false}
        chatError={null}
        onSendMessage={onSendMessage}
        onClearChat={onClearChat}
      />
    );

    expect(screen.getByText(/Cuts PM2.5 exposure by 65%/i)).toBeInTheDocument();

    const input = screen.getByLabelText(/Ask SmogShield/i);
    await user.type(input, 'Can kids play outside?');
    await user.click(screen.getByRole('button', { name: /Send message/i }));

    expect(onSendMessage).toHaveBeenCalledWith('Can kids play outside?');
  });

  it('displays typing indicator and error banner appropriately', () => {
    render(
      <ChatWindow
        city="Lahore"
        messages={[]}
        sending={true}
        chatError="Rate limit exceeded"
        onSendMessage={vi.fn()}
        onClearChat={vi.fn()}
      />
    );

    expect(screen.getByText(/analyzing local AQI/i)).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('Rate limit exceeded');
  });
});
