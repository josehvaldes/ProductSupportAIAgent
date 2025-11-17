import { Image, Text, Button, Modal, Grid } from '@mantine/core';
import type { Product } from "../types/Product";
import { useState } from 'react';
import { ProductDetails } from './ProductDetails';
import { createLogger } from '../utils/logger';



export interface ProductComparisonProps {
  products: Array<Product>;
}

export function ProductComparison({ products } :ProductComparisonProps) {
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [opened, setOpened] = useState(false);
  const log = createLogger('ProductComparison');
  const handleViewDetails = (product: Product) => {
    log.info("ProductGrid View Details clicked for product: ", product.id);
    setSelectedProduct(product);
    setOpened(true);
  };
    return (
        <>
        <Text  c="dimmed">Product Comparison Component</Text>
        <Grid >
            <Grid.Col span={2}>
                <Text>_</Text>
                <Text>Name</Text>
                <Text>Price</Text>
                <Text>Availability</Text>

                
            </Grid.Col>
            { (products && products.length > 0)? products.map(( product, index) => (
                <Grid.Col span={3} key={product.id}>
                    <Text>Product {index+1}</Text>
                    <Text>{product.name}</Text>
                    <Text>${product.price.toFixed(2)}</Text>
                    <Text>{product.availability}</Text>
                    <Image 
                      src={product.image_url}
                        alt={product.name}
                    />
                    <Button 
                      fullWidth 
                        mt="md" 
                        radius="md" 
                        onClick={() => handleViewDetails(product)}
                    >
                        View Details
                    </Button>
                </Grid.Col>
            )):
            <Text c="dimmed">No products to display.</Text
            >}
        </Grid>
        <Modal opened={opened} 
            onClose={() => setOpened(false)} 
            size="sm"
            title="Product Details:"
        >
            {selectedProduct && <ProductDetails product={selectedProduct} />}
        </Modal>
        </>
        );

}