import { Card, Text, Loader } from "@mantine/core";

interface ResponseBoxProps {
  text: string;
  isLoading?: boolean;
}

export function ResponseBox({ text, isLoading = false }: ResponseBoxProps) {
  return (
    <Card shadow="sm" padding="md" radius="md" withBorder>
      {isLoading ? (
        <Loader size="sm" />
      ) : (
        <Text>{text || "No response yet."}</Text>
      )}
    </Card>
  );
}
