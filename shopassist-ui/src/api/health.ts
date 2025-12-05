import { apiRequest } from './apiGeneric';

// Health check response type
export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  service: string;
  version: string;
}


// Specific API functions for your petshop
export const petshopApi = {
  
  // Send a message to your agent/chatbot
  sendMessage: async (message: string): Promise<{ response: string }> => {
    return apiRequest('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },

  // Get Health Check
  healthCheck: async (): Promise<HealthCheckResponse> => {
    return apiRequest('/health/ready');
  },

  // Example: Get pet information
  // getPets: async (): Promise<any[]> => {
  //   return apiRequest('/pets');
  // },

  // getPetById: async (id: string) => {
  //   return apiRequest(`/pets/${id}`);
  // },
};

export default petshopApi;
