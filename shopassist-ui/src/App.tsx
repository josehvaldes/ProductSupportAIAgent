import { useState } from "react";
import {
  AppShell,
  ScrollArea,
  Container,
  Stack,
} from "@mantine/core";
import { InputBox } from "./components/InputBox";
import { ResponseBox } from "./components/ResponseBox";
import { NavBar } from "./components/NavBar";
import { useChat } from "./hooks/useChat";

export default function App() {
  const [response, setResponse] = useState<string>("");
  const { sendMessage, isLoading, error } = useChat();

  const handleSubmit = async (message: string) => {
    const apiResponse = await sendMessage(message);
    if (apiResponse) {
      setResponse(apiResponse);
    } else if (error) {
      setResponse(`Error: ${error}`);
    }
  };

  return (
    <AppShell
      padding="md"
      navbar={{
        width: 200,
        breakpoint: "sm",
        collapsed: { mobile: false },
      }}
    >
      <AppShell.Navbar p="md">
        <NavBar />
      </AppShell.Navbar>

      <AppShell.Main>
        <ScrollArea style={{ height: "100vh" }}>
          <Container size="sm" mt="lg">
            <Stack gap="md">
              <InputBox onSubmit={handleSubmit} isLoading={isLoading} />
              <ResponseBox text={response} isLoading={isLoading} />
            </Stack>
          </Container>
        </ScrollArea>
      </AppShell.Main>
    </AppShell>
  );
}
