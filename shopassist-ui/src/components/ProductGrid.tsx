import { Card, Image, Text, Badge, Button, Group, SimpleGrid, Modal, Stack } from '@mantine/core';
import type { Product } from "../types/Product";
import { useState } from 'react';
import { ProductDetails } from './ProductDetails';
import { createLogger } from '../utils/logger';

export interface ProductGridProps {
  products: Array<Product>;
}

export function ProductGrid({products } :ProductGridProps) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [opened, setOpened] = useState(false);
  const log = createLogger('TestConnectionSection');
  const handleViewDetails = (product: Product) => {
    log.info("ProductGrid View Details clicked for product: ", product.id);
    setSelectedProduct(product);
    setOpened(true);
  };
  return (
    <>    
    <SimpleGrid cols={2} spacing="xl" verticalSpacing="xl" w={"100%"}>

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
            <Stack align="flex-end">
              <Badge color="green">${product.price.toFixed(2)}</Badge>
              <Badge color="red">{product.availability}</Badge>  
            </Stack>
          </Group>
          <Text size="sm" c="dimmed">
            {product.description.substring(0, 60)}...
          </Text>
          <Button 
            fullWidth 
              mt="md" 
              radius="md" 
              onClick={() => handleViewDetails(product)}
          >
            View Details
          </Button>
        </Card>
        )):
        <Text c="dimmed">No products to display.</Text>

      }
    </SimpleGrid>
    <Modal className='Modalclass1'  opened={opened} 
        onClose={() => setOpened(false)} 
        size="sm"
        title="Product Details:"
      >
        {selectedProduct && <ProductDetails product={selectedProduct} />}
    </Modal>
    
    </>
  );
}

