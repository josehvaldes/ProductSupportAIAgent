import { Box, Title, Group, Text, Anchor } from '@mantine/core';
export function NavBar() {
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
    </Box>
  );
}