import { Indicator, Paper, Space, Stack, Text, useMantineTheme } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage as ChatMessageType, ProductSource as ProductSourceType } from '../../api/chat';
import { ProductGrid } from '../ProductGrid';
import { ProductComparison } from '../ProductComparison';
import type { Product } from "../../types/Product";
interface ChatMessageProps {
  message: ChatMessageType;
  sources: ProductSourceType[];
  query_type: string;
}

export function ChatMessage({ message, sources, query_type }: ChatMessageProps) {
  const theme = useMantineTheme();
  const isUser = message.role === 'user';
  const color_indicator = query_type in ['product_search', 'product_details', 'product_comparison'] ? 'blue' : 'green';
  return (
    <Stack>
      <Paper
        p="md"
        style={{
          backgroundColor: isUser 
            ? theme.colors.blue[6] 
            : theme.colors.gray[1],
          color: isUser ? 'white' : 'inherit',
        }}
      >
        <Indicator inline label={query_type}  color={color_indicator} size={12}>
          <Space h="md" />
          <Text size="xs"   >
            {isUser ? 'You' : 'Assistant'}
          </Text>
        </Indicator>
        {isUser ? (
          <Text>{message.content}</Text>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </Paper>

      {/* Render sources if any */}
      {!isUser && (query_type === 'product_search' || 
                  query_type === 'product_details' )
          && sources && sources.length > 0 && (
        <div>
        
        <ProductGrid products={sources.map(source => ({
            id: source.id,
            name: source.name,
            description: source.description,
            category: source.category,
            brand: source.brand,
            image_url: source.image_url,
            product_url: source.product_url,
            price: source.price,
            availability: source.availability,
          } as Product)
        ) 
      } />
        </div>
      )}

      {!isUser && ( query_type === 'product_comparison')
          && sources && sources.length > 0 && (
          <ProductComparison products={sources.map(source => ({
              id: source.id,
              name: source.name,
              description: source.description,
              category: source.category,
              brand: source.brand,
              image_url: source.image_url,
              product_url: source.product_url,
              price: source.price,
              availability: source.availability,
            } as Product)
          ) 
        } />

      )}

      { !isUser && (query_type === 'policy_question'
        || query_type === 'general_support' 
        || query_type === 'out_of_scope' 
        || query_type === 'chitchat'
      ) && sources && sources.length > 0 && (
          <Space h="md" />
      )
      }

     
    </Stack>
  );
}