import { useState } from "react";
import { Textarea, Button, Group } from "@mantine/core";
import { createLogger } from '../utils/logger';
interface InputBoxProps {
  onSubmit: (message: string) => void;
  isLoading?: boolean;
}

export function InputBox({ onSubmit, isLoading = false }: InputBoxProps) {
  const [input, setInput] = useState("");
  const log = createLogger('agent');

  const handleSend = () => {
    if (!input.trim()) return;
    log.info("Submitting message:", input);
    onSubmit(input);
    setInput("");
  };

  return (
    <Group align="end">     
      <Textarea
        value={input}
        onChange={(e) => setInput(e.currentTarget.value)}
        placeholder="Type your message..."
        className="input-textarea"
      />
      <Button onClick={handleSend} loading={isLoading} disabled={isLoading}>
        Send
      </Button>
    </Group>
  );
}
