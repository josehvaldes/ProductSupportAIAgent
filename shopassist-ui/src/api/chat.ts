import { apiRequest } from './apiGeneric';
import type { Product } from '../types/Product';

// API response types
export interface ApiResponse {
  conversation_id: string;
  reply: string;
  created_time: string;
  suggestions?: Array<Product>;    
}

export const chatApi = {
  // Send a message to your agent/chatbot
    sendMessage: async (message: string): Promise<ApiResponse> => {
      
      const body = {
        message: message,
        conversation_id: "",
        user_id: ""
      }
      return apiRequest('/dummy_chat', {
        method: 'POST',
        body: JSON.stringify(body),
        });

    }
};

export default chatApi;