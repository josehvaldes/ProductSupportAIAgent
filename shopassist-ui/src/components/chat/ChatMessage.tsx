import { Paper, Stack, Text, useMantineTheme } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage as ChatMessageType, ProductSource as ProductSourceType } from '../../api/chat';
import { ProductSource } from './ProductSource';
import { ProductGrid } from '../ProductGrid';
import type { Product } from "../../types/Product";
interface ChatMessageProps {
  message: ChatMessageType;
  sources: ProductSourceType[];
}

export function ChatMessage({ message, sources }: ChatMessageProps) {
  const theme = useMantineTheme();
  const isUser = message.role === 'user';

  return (
    <Stack>
      <Paper
        p="md"
        style={{
          maxWidth: '70%',
          backgroundColor: isUser 
            ? theme.colors.blue[6] 
            : theme.colors.gray[1],
          color: isUser ? 'white' : 'inherit',
        }}
      >
        <Text size="xs" color={isUser ? 'gray.2' : 'dimmed'} mb={4}>
          {isUser ? 'You' : 'Assistant'}
        </Text>
        
        {isUser ? (
          <Text>{message.content}</Text>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </Paper>
      {/* Render sources if any */}
      
      {!isUser && sources && sources.length > 0 && (
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
      )}
        {/* <div style={{ marginLeft: 8 }}> 
          {sources.map((source, index) => (
            <ProductSource key={index} source={source} />
          ))
          }
        </div>
      )
      } */}
      
    </Stack>
  );
}