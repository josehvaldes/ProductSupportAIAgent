import { useState } from 'react';
import { Textarea, Button, Group, Text } from '@mantine/core';
// import { IconSend } from '@tabler/icons-react';
import type { KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const MAX_LENGTH = 500;

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const remainingChars = MAX_LENGTH - message.length;
  const isNearLimit = remainingChars < 50;

  return (
    <div>
      <Textarea
        placeholder="Ask me about products... (Press Enter to send)"
        value={message}
        onChange={(e) => setMessage(e.currentTarget.value)}
        onKeyDown={handleKeyPress}
        disabled={disabled}
        minRows={2}
        maxRows={4}
        maxLength={MAX_LENGTH}
        style={{ marginBottom: 8 }}
      />
      
      <Group >
        <Text 
          size="xs" 
          color={isNearLimit ? 'red' : 'dimmed'}
        >
          {remainingChars} characters remaining
        </Text>
        
        <Button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          loading={disabled}
        >
          Send
        </Button>
      </Group>
    </div>
  );
}