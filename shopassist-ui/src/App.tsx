import {
  AppShell,
  Box,
} from "@mantine/core";
import { NavBar } from "./components/NavBar";
import { TestConnectionSection } from "./components/TestConnectionSection";

import { ChatContainerExt } from "./components/chat/ChatContainerExt";

import { SearchContainer } from "./components/SearchContainer";
import { useLocalStorage } from "./hooks/useLocalStorage";
import { Notifications } from '@mantine/notifications';

type ActiveView = 'search' | 'settings' | 'help' | 'chat-ext';

export default function App() {
  const [activeView, setActiveView] = useLocalStorage<ActiveView>('shopassist-active-view', 'chat-ext');

  const renderMainContent = () => {
    switch (activeView) {
      case 'search':
        return <SearchContainer />;
      case 'settings':
        return <div>Settings Container</div>;
      case 'help':
        return <div>Help Container</div>;
      case 'chat-ext':
        return <ChatContainerExt />;
      
    }
  };

  return (
    <AppShell
      padding="md"
      navbar={{
        width: 250,
        breakpoint: "sm",
      }}    
    >
      <AppShell.Navbar p="md" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Notifications position="top-right" />
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
