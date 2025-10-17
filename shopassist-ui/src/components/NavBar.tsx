import { useState } from "react";
import { Box, Title, Text} from '@mantine/core';
import { TestConnectionButton } from './TestConnectionButton';
import { healthCheck } from "../hooks/healthCheck";
import { createLogger } from '../utils/logger';

export function NavBar() {

  const [response, setResponse] = useState<string>("");
  const { sendMessage, isLoading, error } = healthCheck();
  const log = createLogger('NavBar');
  const handleSubmit = async () => {
    log.info("NavBar: Send health check");
    const apiResponse = await sendMessage();
    if (apiResponse) {
      setResponse(apiResponse);
    } else if (error) {
      setResponse(`Error: ${error}`);
    }
  };

  return (
    <Box
      component="nav"
    >
      <Title order={3} mb="md">
        Agent UI
      </Title>
      <Text size="sm" c="dimmed">
        Specialized Assistant
      </Text>
      <TestConnectionButton 
        onSubmit={handleSubmit} 
        isLoading={isLoading}
        text={response}
        />
    </Box>
  );
}