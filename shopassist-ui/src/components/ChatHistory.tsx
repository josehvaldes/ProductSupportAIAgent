
import {Group, NavLink } from '@mantine/core';

export function ChatHistory() {
  return (
    <Group>
        <p>Chat History </p>
        <NavLink label="Chat with Support" />
        <NavLink label="Order Inquiry" />
        <NavLink label="Product Information" />
    </Group>
  );
}