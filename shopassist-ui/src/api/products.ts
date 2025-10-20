import { apiRequest } from './apiGeneric';
import type { Product } from '../types/Product';

// Specific API functions for products
export const productApi = {
  // Fetch all products
  getProducts: async (): Promise<Product[]> => {
    return apiRequest('/products');
  },

    // Fetch a product by ID
  getProductById: async (id: string): Promise<Product> => {
    return apiRequest(`/products/${id}`);
  },
  getProductsByCategory: async (category: string): Promise<Product[]> => {
    return apiRequest(`/products/search/category/${encodeURIComponent(category)}`);    
  },
  getProductsInPriceRange: async (minPrice: number, maxPrice: number): Promise<Product[]> => {
    return apiRequest(`/products/search/price?min_price=${minPrice}&max_price=${maxPrice}`);
  }
};

export default productApi;