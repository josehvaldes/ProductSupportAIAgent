import React from 'react';
import { Alert, Code } from '@mantine/core';

type Props = { children: React.ReactNode };
type State = { hasError: boolean; error?: Error };

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Replace with Sentry/LogRocket/etc. if needed
    console.error('React error boundary caught', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert color="red" title="Something went wrong">
          <Code block>{this.state.error?.message ?? 'Unknown error'}</Code>
        </Alert>
      );
    }
    return this.props.children;
  }
}