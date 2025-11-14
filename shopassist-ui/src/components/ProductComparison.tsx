import { Card, Image, Text, Badge, Button, Group, SimpleGrid, Modal, Stack, Grid, Space } from '@mantine/core';
import type { Product } from "../types/Product";
import { useState } from 'react';
import { ProductDetails } from './ProductDetails';
import { createLogger } from '../utils/logger';



export interface ProductComparisonProps {
  products: Array<Product>;
}

export function ProductComparison({ products } :ProductComparisonProps) {

    return (
        <>
        <Text  c="dimmed">Product Comparison Component</Text>
        <Grid >
            <Grid.Col span={3}>
                <Text>_</Text>
                <Text>Name</Text>
                <Text>Price</Text>
                <Text>Availability</Text>

                
            </Grid.Col>
            { (products && products.length > 0)? products.map(( product, index) => (
                <Grid.Col span={4} key={product.id}>
                    <Text>Product {index+1}</Text>
                    <Text>{product.name}</Text>
                    <Text>${product.price.toFixed(2)}</Text>
                    <Text>{product.availability}</Text>
                    <Image 
                      src={product.image_url}
                        alt={product.name}
                    />
                    
                </Grid.Col>
            )):
            <Text c="dimmed">No products to display.</Text
            >}
        </Grid>
        </>
        );

}