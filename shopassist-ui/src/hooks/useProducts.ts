import { useState, useCallback, useEffect } from 'react';
import { createLogger } from '../utils/logger';
import { productApi } from '../api/products';
import type { Product } from '../types/Product';

interface UseProductState {
    // Define state properties and methods for product view model here
    isLoading?: boolean;
    error?: string | null;
    getProductById?: (id: string) => Promise<any | null>;
    getProductsByCategory?: (id: string) => Promise<any | null>;
    getProductsInPriceRange?: (minPrice: number, maxPrice: number) => Promise<any | null>;
}

export function useProducts():UseProductState {

    const log = createLogger('productsViewModel');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const getProductById = useCallback(async (id: string): Promise<Product | null> => {
        
        if (!id.trim())
            return null;
        
        setIsLoading(true);
        setError(null);

        try
        {
            log.info("Sending product request to API:", id);
            // Placeholder for actual API call
            const res = await productApi.getProductById(id);
            log.info("Received response from API: ", res);
            return res;
        } catch (err) {
            const errorMessage = err instanceof Error 
                ? err.message
                : 'An unexpected error occurred';
            setError(errorMessage);
            console.error('Products ViewModel API error:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);


    const getProductsByCategory = useCallback(async (category: string): Promise<Product[] | null> => {
        try {
            setIsLoading(true);
            setError(null);
            const result = await productApi.getProductsByCategory(category);
            return result;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch products by category');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getProductsInPriceRange = useCallback(async (minPrice: number, maxPrice: number): Promise<Product[] | null> => {
        try {
            setIsLoading(true);
            setError(null);
            const result = await productApi.getProductsInPriceRange(minPrice, maxPrice);
            return result;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch products in price range');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        // Placeholder for future side effects or data fetching logic
        console.log("Products ViewModel initialized");
    }, []);

    // Placeholder for future product view model logic
    return {
        isLoading,
        error,
        getProductById,
        getProductsByCategory,
        getProductsInPriceRange
    };
}

