import { apiRequest } from './apiGeneric';
import type { Product } from '../types/Product';

// API response types
export interface ApiResponse {
  conversation_id: string;
  reply: string;
  created_time: string;
  suggestions?: Array<Product>;    
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  query_type?: 'product_search' | 
                'product_details' | 
                'product_comparison' |
                'policy_question'|
                'general_support' | 
                'chitchat' | 
                'out_of_scope' | 
                'follow_up';
}

export interface ProductSource {
  type: 'product';
  id: string;
  name: string;
  description: string;
  category: string;
  brand: string;
  image_url: string;
  product_url: string;
  price: number;
  availability: string;
  relevance_score: number;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  sources: ProductSource[];
  query_type: 'product_search' | 
              'product_details' | 
              'product_comparison' |
              'policy_question'|
              'general_support' | 
              'chitchat' | 
              'out_of_scope' | 
              'follow_up';

  metadata: {
    query_type_confidence: number;
    num_sources: number;
    tokens:number;
    cost: number;
  };
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}



export const chatApi = {

  /**
     * Send a message and get AI response
     * @param message 
     * @param sessionId 
     * @returns 
     */
    sendMessage: async (
        message: string,
        sessionId?: string
      ): Promise<ChatResponse> => {

      const response = await apiRequest<ChatResponse>('/chat/dumbmessage', {
          method: 'POST',
          body: JSON.stringify({
          message,
          session_id: sessionId,
        })
      });

      return response;
    },
    /**
   * Get conversation history for a session
   */
    getChatHistory: async (sessionId: string): Promise<ChatHistoryResponse> => {
      const response = await apiRequest<ChatHistoryResponse>(
        `/chat/history/${sessionId}`
      );
      return response;
    },
};

export default chatApi;