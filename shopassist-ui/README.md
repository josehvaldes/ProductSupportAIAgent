# ShopAssist UI

A modern React-based chat interface for the ShopAssist AI product support agent.

## Overview

ShopAssist UI is a responsive web application built with React, TypeScript, and Vite that provides an intuitive chat interface for customers to interact with the AI-powered product support system.

## Features

- 💬 Real-time chat interface with AI assistant
- 🔍 Product search and recommendations
- 📋 Product comparison view
- 🎨 Modern UI built with Mantine components
- 📱 Responsive design for mobile and desktop
- 🔄 Session persistence with conversation history
- ⚡ Fast development and build with Vite

## Tech Stack

- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **UI Library**: Mantine v8
- **Icons**: Tabler Icons
- **Markdown**: React Markdown
- **State Management**: React Hooks

## Prerequisites

- Node.js 18 or higher
- npm or yarn

## Getting Started

### 1. Clone the repository

```bash
cd shopassist-ui
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

For Docker deployment:
```env
VITE_API_BASE_URL=http://shopassist-api:8000/api/v1
```

### 4. Run the development server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:docker` - Build for Docker (skips TypeScript checking)
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Project Structure

```
shopassist-ui/
├── src/
│   ├── components/         # React components
│   │   ├── chat/          # Chat-related components
│   │   ├── navigation/    # Navigation components
│   │   └── product/       # Product display components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API service layer
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.tsx            # Main application component
│   └── main.tsx           # Application entry point
├── public/                # Static assets
├── .env                   # Environment variables
├── Dockerfile             # Docker configuration
└── package.json           # Dependencies and scripts
```

## Key Components

### ChatContainerExt
Main chat interface component with message display and input.

### ProductComparison
Side-by-side product comparison view.

### NavBar
Navigation component for switching between views.

## Docker Deployment

### Build Docker image

```bash
docker build -t shopassist-ui:1.0 .
```

### Run with Docker Compose

```bash
# From project root
docker-compose up -d shopassist-ui
```

The UI will be available at `http://localhost:8080`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

## API Integration

The UI communicates with the ShopAssist API for:
- Chat messages and AI responses
- Product search and retrieval
- Session management
- Conversation history

API service layer is located in `src/services/api.ts`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding new components

```bash
# Create component file
src/components/MyComponent.tsx
```

### Code style

This project uses ESLint for code quality. Run linting with:

```bash
npm run lint
```

## Troubleshooting

### API connection issues

Ensure the backend API is running and the `VITE_API_BASE_URL` is correctly set in `.env`

### Build errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port already in use

Change the dev server port in `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 5173  
  }
})
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run linting: `npm run lint`
4. Build to verify: `npm run build`
5. Submit a pull request

## License

This project is part of the ShopAssist AI Product Support Agent system.

## Related Projects

- [ShopAssist API](../shopassist-api/README.md) - Backend FastAPI service

## Execution:
npm run dev

## Configuration
update the .env file according to your API configuration
VITE_API_BASE_URL

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
