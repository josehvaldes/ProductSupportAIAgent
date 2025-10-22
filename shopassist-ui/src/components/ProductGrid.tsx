import { Card, Image, Text, Badge, Button, Group } from '@mantine/core';
import type { Product } from "../types/Product";

interface ProductGridProps {
  products: Array<Product>;
}

export function ProductGrid({products } :ProductGridProps) {

  return (
    <Group wrap="wrap" justify="center">

      { (products && products.length > 0)? products.map((product) => (
        <Card shadow="sm" padding="lg" radius="md" withBorder className="product-card" mt="md" w={300} mx="auto" key={product.id}>
          <Card.Section>
            <Image 
              src={product.image_url}  
              height={160} 
              alt={product.name}>
                </Image>
          </Card.Section>
          <Group justify="space-between" mt="md" mb="xs">
            <Text fw={500}>{product.name}</Text>
            <Badge color="pink">On Sale</Badge>
          </Group>
          <Text size="sm" c="dimmed">
            {product.description}
          </Text>
          <Button color="blue" fullWidth mt="md" radius="md" component="a" href={product.product_url} target="_blank" rel="noopener noreferrer">
            View Details
          </Button>
        </Card>
        )):
        <Text c="dimmed">No products to display.</Text>

      }
    </Group>

    

  );
}