import { useState, useCallback } from 'react';
import { petshopApi, type HealthCheckResponse } from '../api/health';
import { createLogger } from '../utils/logger';
import { ApiError } from '../api/apiError';

interface HealthCheckState {
  isLoading: boolean;
  error: string | null;
  sendMessage: () => Promise<string | null>;
}
export function healthCheck(): HealthCheckState {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const log = createLogger('healthCheck');
  const sendMessage = useCallback(async (): Promise<string | null> => {

    setIsLoading(true);
    setError(null);

    try {
      log.info("Sending health check to API:");
      const res: HealthCheckResponse = await petshopApi.healthCheck();
      log.info("Received response from API:", res);
      
      // Now you can access the properties directly
      if (res.status !== 'ready') {
        setError(`Service is not healthy. Status: ${res.status}`);
        return `Agent not healthy. V: ${res.version}`;
      }

      log.info(`Service is healthy. Version: ${res.version}, Timestamp: ${res.timestamp}`);
      return `Agent is healthy. V:${res.version}`;
      
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'An unexpected error occurred';
      setError(errorMessage);
      console.error('Health check API error:', err);
      return "Agent not Healthy. Internal Error";
    } finally {
      setIsLoading(false);
    }
  }, []);


  return {
    isLoading,
    error,
    sendMessage: sendMessage,
  };

}