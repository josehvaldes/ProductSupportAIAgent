import {
  ScrollArea,
  Container,
  Stack,
} from "@mantine/core";
import { InputBox } from "./InputBox";
import { ResponseBox } from "./ResponseBox";
import { createLogger } from '../utils/logger';
import { useChat } from "../hooks/useChat";
import { useState } from "react";
import { ProductGrid } from "./ProductGrid";
import type { Product } from "../types/Product";

export function ChatContainer() {
  
  const [response, setResponse] = useState<string>("");
  const [products, setProducts] = useState<Product[]>([]);
  
  const { sendMessage, isLoading, error } = useChat();
  const log = createLogger('TestConnectionSection');

  const onSubmit = async (message: string) => {
    log.info("TestConnectionSection: Send health check");
    const apiResponse = await sendMessage(message);
    if (apiResponse) {
      setResponse(apiResponse.reply);
      const products = apiResponse.products || [];
      setProducts(products);
      log.info(`Received ${products.length} product recommendations.`);
    } else if (error) {
      setResponse(`Error: ${error}`);
    }
  };

  return (
    <ScrollArea style={{ height: "100vh" }}>
      <Container size="sm" mt="lg">
        <p>Welcome to ShopAssist</p>
        <Stack gap="md">
          <InputBox onSubmit={onSubmit} isLoading={isLoading} />
          <ResponseBox text={response} isLoading={isLoading} />
          <ProductGrid products={products} />
        </Stack>
      </Container>
    </ScrollArea>
  );
}