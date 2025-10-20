export interface Product {
    id: string;
    name: string;
    description: string;
    price: number;
    category: string;
    brand: string;
    rating: number;
    review_count: number;
    product_url: string;
    image_url: string;
    category_full: string;
    availability: string;
}

/**
 * "id": "2",
    "name": "Test Product",
    "description": "A product for testing",
    "category": "Testing",
    "price": "19.99",
    "brand": "TestBrand",
    "rating": "4.5",
    "review_count": "10",
    "product_url": "http://example.com/product/test123",
    "image_url": "http://example.com/product/test123/image.jpg",
    "category_full": "Testing/Unit Tests",
    "availability": "In Stock"
 */