import { Card, Text, Badge, Button, Group } from '@mantine/core';
import type { ProductSource as ProductSourceType } from '../../api/chat';
import { useNavigate } from 'react-router-dom';

interface ProductSourceProps {
  source: ProductSourceType;
}

export function ProductSource({ source }: ProductSourceProps) {
  //const navigate = useNavigate();

  const handleViewProduct = () => {
    //navigate(`/products/${source.id}`);
    console.log(`Navigating to product URL: ${source.product_url}`);
  };

  return (
    <Card shadow="sm" p="sm" withBorder>
      <Group mb="xs">
        <Text size="sm" lineClamp={1}>
          {source.name}
        </Text>
        <Badge color="blue" variant="light">
          {(source.relevance_score * 100).toFixed(0)}% match
        </Badge>
      </Group>

      <Text size="xl" color="blue" mb="xs">
        ${source.price.toFixed(2)}
      </Text>

      <Button 
        fullWidth 
        variant="light" 
        size="xs"
        onClick={handleViewProduct}
      >
        View Product
      </Button>
    </Card>
  );
}