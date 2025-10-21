import { use, useState } from "react";
import { Box, Textarea } from "@mantine/core";
import { Card, Image, Text, Badge, Button, Group } from '@mantine/core';
import { useProducts } from "../hooks/useProducts";
import type { Product } from "../types/Product";

export function SearchContainer(){
    const [input, setInput] = useState("");
    const [product, setProduct] = useState<Product>({} as Product);
    const { isLoading, error, getProductById, getProductsByCategory, getProductsInPriceRange } = useProducts();
    const onSubmit = async (id: string) => {
        // Implement search submission logic here
        console.log("Search submitted:", id);
        const product = await getProductById?.(id);
        console.log("Product fetched:", product);
        setProduct(product);
    } 
    
    return (
        <Box p="md" className="search-container">
            <Group align="end" justify="center">
                <Textarea  disabled={isLoading}
                    placeholder="Search for products..."
                    value={input}
                    onChange={(e) => setInput(e.currentTarget.value) }
                />
                <Button onClick={() => onSubmit(input)} disabled={isLoading}>
                    Search
                </Button>
            </Group>
            {
                product && product.id ?
                (<Card shadow="sm" padding="lg" radius="md" withBorder className="search-result-card" mt="md" w={300} mx="auto">
                    <Card.Section>
                        <Image
                            src={product.image_url}  
                            height={160}
                            alt="Search Result"
                        />
                    </Card.Section>
                    <Group justify="space-between" mt="md" mb="xs">
                        <Text fw={500}>{product.name}</Text>
                        <Badge color="pink">On Sale</Badge>
                    </Group>

                    <Text size="sm" c="dimmed">
                        {product.description}
                    </Text>

                    <Button color="blue" fullWidth mt="md" radius="md">
                        View Details
                    </Button>
                </Card>):
                <p>...</p>
            }
        </Box>        
    );
};