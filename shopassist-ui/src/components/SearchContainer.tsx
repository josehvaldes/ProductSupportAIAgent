import { useState } from "react";
import { Box, Textarea } from "@mantine/core";
import { Card, Image, Text, Badge, Button, Group } from '@mantine/core';

export function SearchContainer(){
    const [input, setInput] = useState("");
    const onSubmit = async (query: string) => {
        // Implement search submission logic here
        console.log("Search submitted:", query);
    }

    return (
        <Box p="md">
            <Group align="end">
                <Textarea 
                    value={input}
                    onChange={(e) => setInput(e.currentTarget.value)}
                />
                <Button onClick={() => onSubmit(input)}>
                    Search
                </Button>

            </Group>

            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Card.Section>
                    <Image
                        src="https://m.media-amazon.com/images/I/41V5FtEWPkL._SX300_SY300_QL70_FMwebp_.jpg"
                        height={160}
                        alt="Search Result"
                    />
                </Card.Section>
                <Group justify="space-between" mt="md" mb="xs">
                    <Text fw={500}>Norway Fjord Adventures</Text>
                    <Badge color="pink">On Sale</Badge>
                </Group>

                <Text size="sm" c="dimmed">
                    With Fjord Tours you can explore more of the magical fjord landscapes with tours and
                    activities on and around the fjords of Norway
                </Text>

                <Button color="blue" fullWidth mt="md" radius="md">
                    Book classic tour now
                </Button>
            </Card>

        </Box>
        
    );
};