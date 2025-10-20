import { useState, useCallback } from 'react';
import { petshopApi} from '../api/health';
import { createLogger } from '../utils/logger';
import { ApiError } from '../api/apiError';

interface UseChatState {
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<string | null>;
}

export function useChat(): UseChatState {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const log = createLogger('agent');
  const sendMessage = useCallback(async (message: string): Promise<string | null> => {
    if (!message.trim()) return null;

    setIsLoading(true);
    setError(null);

    try {
      log.info("Sending message to API:", message);
      const response = await petshopApi.sendMessage(message);
      log.info("Received response from API:", response.response);
      return response.response;
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
