import { Badge, Card, Group, Image, Text } from "@mantine/core";
import type { Product } from "../types/Product";


export interface ProductDetailsProps {
    product: Product;
}

export function ProductDetails({ product }: ProductDetailsProps) {
    return (
        <>
        <Card shadow="sm" padding="lg" radius="md" w={"100%"}
         key={product.id}>
            <Card.Section mb="md" w={"100%"}>
                <Image 
                    src={product.image_url}  
                    height={250} 
                    alt={product.name}>
                    </Image>
            </Card.Section>
            <Group justify="space-between" mt="md" mb="xs">
                <Text fw={500}>{product.name}</Text>
                <Badge color="green">${product.price.toFixed(2)}</Badge>
            </Group>
            <Group justify="space-between" mt="md" mb="xs">
                <Text fw={500} >Rating: {product.rating}</Text>                
                <Badge color="pink">{product.availability}</Badge>
            </Group>
            <Group justify="space-between" mt="md" mb="xs">
                <Text fw={500}>
                    Category:
                </Text>
                <Text size="sm" c="dimmed">
                    {product.category_full}
                </Text>
            </Group>
            
            <Text size="sm" c="dimmed">
                {product.description}
            </Text>
        </Card>
        </>
    );
}