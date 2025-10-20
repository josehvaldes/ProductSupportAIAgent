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

export function ChatContainer() {
  
  const [response, setResponse] = useState<string>("");
  const log = createLogger('TestConnectionSection');
  const { sendMessage, isLoading, error } = useChat();

  const onSubmit = async (message: string) => {
    log.info("TestConnectionSection: Send health check");
    const apiResponse = await sendMessage(message);
    if (apiResponse) {
      setResponse(apiResponse);
    } else if (error) {
      setResponse(`Error: ${error}`);
    }
  };

  return (
    <ScrollArea style={{ height: "100vh" }}>
      <Container size="sm" mt="lg">
        <Stack gap="md">
          <InputBox onSubmit={onSubmit} isLoading={isLoading} />
          <ResponseBox text={response} isLoading={isLoading} />
        </Stack>
      </Container>
    </ScrollArea>
  );
}