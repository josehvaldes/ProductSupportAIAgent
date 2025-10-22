import { useState, useCallback } from 'react';
import { chatApi } from '../api/chat';
import { createLogger } from '../utils/logger';
import { ApiError } from '../api/apiError';

interface UseChatState {
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<any | null>;
}

export function useChat(): UseChatState {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const log = createLogger('usechat');
  const sendMessage = useCallback(async (message: string): Promise<any | null> => {
    if (!message.trim()) return null;

    setIsLoading(true);
    setError(null);

    try {
      log.info("Sending message to API:", message);
      const response = await chatApi.sendMessage(message);
      // do any transformation if needed
      const transformedResponse = {
        reply: response.reply, // example transformation
        products: response.suggestions || [],
      }
      return transformedResponse;
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'An unexpected error occurred';
      setError(errorMessage);
      console.error('Chat API error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    sendMessage,
  };
}
