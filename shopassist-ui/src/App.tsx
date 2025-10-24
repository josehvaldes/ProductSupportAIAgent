import {
  AppShell,
  Box,
} from "@mantine/core";
import { NavBar } from "./components/NavBar";
import { TestConnectionSection } from "./components/TestConnectionSection";
import { ChatContainer } from "./components/ChatContainer";
import { SearchContainer } from "./components/SearchContainer";
import { useLocalStorage } from "./hooks/useLocalStorage";

type ActiveView = 'chat' | 'search' | 'settings' | 'help';

export default function App() {
  const [activeView, setActiveView] = useLocalStorage<ActiveView>('shopassist-active-view', 'chat');

  const renderMainContent = () => {
    switch (activeView) {
      case 'search':
        return <SearchContainer />;
      case 'settings':
        return <div>Settings Container</div>;
      case 'help':
        return <div>Help Container</div>;
      case 'chat':
        return <ChatContainer />;
      
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
      <AppShell.Navbar p="md" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box style={{ flex: 1 }}>
          <NavBar activeView={activeView} onViewChange={setActiveView} />
        </Box>
        <TestConnectionSection />
      </AppShell.Navbar>

      <AppShell.Main>
        {renderMainContent()}
      </AppShell.Main>
    </AppShell>
  );
}
