import { useState, useEffect, useRef } from 'react';
import { Paper, ScrollArea, Stack, Text, Loader, Container } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { chatApi } from '../../api/chat';
import type { ChatMessage as ChatMessageType, ProductSource } from '../../api/chat';
import { v4 as uuidv4 } from 'uuid';
import { createLogger } from '../../utils/logger';

// Extended message type to include sources
interface ExtendedChatMessage extends ChatMessageType {
  sources?: ProductSource[];
}
export function ChatContainerExt() {
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const viewport = useRef<HTMLDivElement>(null);
  const logger = createLogger('chat-container');
  const initialized = useRef(false);  //
   // Initialize session
  useEffect(() => {
    console.log("ChatContainerExt useEffect called");
    // Prevent double execution in Strict Mode
    if (initialized.current) {
      return;
    }
    initialized.current = true;

    // For testing, use fixed session ID
    // let storedSessionId = "58ca3bbb-1fbc-4cfa" 
    // setSessionId(storedSessionId );   

    // Get session from localStorage or create new
    let storedSessionId = localStorage.getItem('chat_session_id');
    if (!storedSessionId) {
      storedSessionId = uuidv4().slice(-12);
      logger.info("Creating new session ID:", storedSessionId);
      localStorage.setItem('chat_session_id', storedSessionId);
      setSessionId(storedSessionId );   
    }
    else{
      // Load history
      setSessionId(storedSessionId );   
      logger.info("loading history for session ID:", storedSessionId);
      loadHistory(storedSessionId);  
    }
    
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (viewport.current) {
      viewport.current.scrollTo({
        top: viewport.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);


  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message immediately
    const userMessage: ExtendedChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call API
      const response = await chatApi.sendMessage(message, sessionId);

      // Add assistant response WITH sources
      const assistantMessage: ExtendedChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        sources: response.sources,  // ← Store sources here
        query_type: response.query_type,
      };
      logger.info("Received assistant message:", assistantMessage);
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error: any) {
      console.error('Error sending message:', error);
      
      notifications.show({
        title: 'Error',
        message: error.response?.data?.detail || 'Failed to send message',
        color: 'red',
      });

      // Remove user message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const loadHistory = async (sid: string) => {
    try {
      console.log("Loading history for session ID:", sid);
      if (!sid) 
      {
        return;
      }      
      const history = await chatApi.getChatHistory(sid);
      setMessages(history.messages);
    } catch (error) {
      console.error('Error loading history:', error);
      // Silent fail - probably no history yet
    }
  };


  const handleNewConversation = () => {
    //get last 12 chars of uuid
    const newSessionId = uuidv4().slice(-12);
    logger.info("Creating new session ID:", newSessionId);
    localStorage.setItem('chat_session_id', newSessionId);
    setSessionId(newSessionId);
    setMessages([]);
    
    notifications.show({
      title: 'New Conversation',
      message: 'Started a new conversation',
      color: 'blue',
    });
  };


  return (
    <Paper shadow="sm" p="md" 
          style={{ height: '100%', 
              display: 'flex', 
              flexDirection: 'column', 
              width: '100%'
              }}>
      <Stack style={{ flex: 1, overflow: 'hidden' }}>
        {/* ... header ... */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Container style={{ padding: 0, margin: 0 }}>
            <Text size="lg" >Chat Assistant</Text>
            <Text>Session Id: {sessionId}</Text>
          </Container>
          
          <Text 
            size="sm" 
            td ="underline"
            style={{ cursor: 'pointer' }}
            onClick={handleNewConversation}
          >
            Start New Chat
          </Text>
        </div>

        {/* Messages */}
        <ScrollArea style={{ flex: 1 }} viewportRef={viewport}>
          <Stack >
            {messages.length === 0 && (
              <Text color="dimmed" mt="xl">
                Start a conversation by asking about products!
              </Text>
            )}
            
            {messages.map((msg, index) => (
              <ChatMessage 
                key={index} 
                message={msg}
                sources={msg.sources || []}
                query_type={msg.query_type || 'user'}
              />
            ))}

            {/* ... loading indicator ... */}
            {isLoading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Loader size="sm" />
                <Text size="sm" color="dimmed">Thinking...</Text>
              </div>
            )}
          </Stack>
        </ScrollArea>

                {/* ... input ... */}
        <ChatInput 
          onSend={handleSendMessage} 
          disabled={isLoading}
        />
        
      </Stack>
    </Paper>
  );
}