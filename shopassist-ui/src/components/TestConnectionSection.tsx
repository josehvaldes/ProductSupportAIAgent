import { useState } from "react";
import { Box } from '@mantine/core';
import { healthCheck } from "../hooks/healthCheck";
import { createLogger } from '../utils/logger';
import { Button, Group, TextInput } from "@mantine/core";

export function TestConnectionSection() {
  const [response, setResponse] = useState<string>("");
  const { sendMessage, isLoading, error } = healthCheck();
  const log = createLogger('TestConnectionSection');

  const handleSubmit = async () => {
    log.info("TestConnectionSection: Send health check");
    const apiResponse = await sendMessage();
    if (apiResponse) {
      setResponse(apiResponse);
    } else if (error) {
      setResponse(`Error: ${error}`);
    }
  };

  return (
    <Box mt="auto">
      <Group align="end">
        <TextInput 
            value={response || "..."}
            className="test-connection-message"
            readOnly={true}
            disabled={true}
        />
        <Button onClick={handleSubmit} 
            loading={isLoading}
            disabled={isLoading}
            className="test-connection-button"
            >
            Test Agent Connection
        </Button>        
        </Group>
    </Box>
  );
}
