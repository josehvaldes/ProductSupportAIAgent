// API configuration and base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

// Health check response type
export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  service: string;
  version: string;
  database: string;
}

// Error handling
export class ApiError extends Error {
  status: number;
  response: any | undefined;

  constructor(
    message: string,
    status: number,
    response?: any
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || `HTTP error! status: ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error occurred', 0, error);
  }
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
    return apiRequest('/health');
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
