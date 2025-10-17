import { useState } from "react";
import { Textarea, Button, Group, TextInput } from "@mantine/core";
import { createLogger } from '../utils/logger';

interface TestConnectionButtonProps {
  onSubmit: (message: string) => void;
  isLoading?: boolean;
  text?: string;
}

export function TestConnectionButton({ onSubmit, text = ".", isLoading = false }: TestConnectionButtonProps) {
  const [input, setInput] = useState("");
  const log = createLogger('agent');

  const handleClick = () => {
    log.info("Submitting message:", input);
    onSubmit(input);
    setInput("");
  };

  return (
    <Group align="end">
      <Button onClick={handleClick} 
        loading={isLoading}
        disabled={isLoading}
        className="test-connection-button"
        >
        Test Agent Connection
      </Button>
      <TextInput 
        value={text || "..."}
        onChange={(e) => setInput(e.currentTarget.value)}
        className="test-connection-message"
        readOnly={true}
        disabled={true}
      />
    </Group>
  );
}