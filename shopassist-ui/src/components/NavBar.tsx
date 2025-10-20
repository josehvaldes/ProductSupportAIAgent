import { Box, Title, Text, NavLink} from '@mantine/core';

type ActiveView = 'chat' | 'search' | 'settings' | 'help';

interface NavBarProps {
  activeView: ActiveView;
  onViewChange: (view: ActiveView) => void;
}

export function NavBar({ activeView, onViewChange }: NavBarProps) {
  return (
    <Box
      component="nav"
    >
      <Title order={3} mb="md">
        Agent UI
      </Title>
      <Text size="sm" c="dimmed">
        Specialized Assistant
      </Text>      <Box mb="md" className="nav-bar-options" >
        {/* Future navigation options can be added here */}
        <NavLink 
          label="Chat" 
          active={activeView === 'chat'}
          onClick={() => onViewChange('chat')}
        />
        <NavLink 
          label="Search" 
          active={activeView === 'search'}
          onClick={() => onViewChange('search')}
        />
        <NavLink 
          label="Settings" 
          active={activeView === 'settings'}
          onClick={() => onViewChange('settings')}
        />
        <NavLink 
          label="Help" 
          active={activeView === 'help'}
          onClick={() => onViewChange('help')}
        />
      </Box>
    </Box>
  );
}