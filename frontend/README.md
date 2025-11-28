# Mudda AI Workflow Frontend

A Next.js frontend application for managing AI-powered workflows and API components.

## Features

- **Workflows Page**: View, generate, and manage workflow plans
- **Components Page**: Create and manage API components
- **Reusable Components**: Modern, robust UI components built with React and Tailwind CSS
- **API Integration**: Seamless connection to the FastAPI backend

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running (default: http://localhost:8081)

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Configure the API URL (optional):
   - Create a `.env.local` file in the frontend directory
   - Set `NEXT_PUBLIC_API_URL=http://localhost:8081` (or your backend URL)

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── workflows/         # Workflows page
│   ├── components/        # Components page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # Reusable UI components
│   ├── Button.tsx        # Button component
│   ├── Modal.tsx         # Modal component
│   ├── Table.tsx         # Table component
│   └── Navigation.tsx    # Navigation component
├── lib/                   # Utilities
│   └── api.ts            # API client and types
└── package.json
```

## Components

### Reusable Components

- **Button**: Flexible button component with variants and loading states
- **Modal**: Accessible modal dialog component
- **Table**: Generic table component with customizable columns and actions
- **Navigation**: Top navigation bar with active state management

### Pages

- **Workflows**: 
  - Table of all workflows
  - Generate workflow button
  - Info button to view workflow details in a modal
  
- **Components**:
  - Table of all components
  - Create component button
  - Info button to view component details in a modal

## API Integration

The frontend connects to the backend API through the `lib/api.ts` module, which provides:

- `workflowApi`: Methods for workflow operations (generate, getAll, getById)
- `componentApi`: Methods for component operations (create, getAll, getById)

## Building for Production

```bash
npm run build
npm start
```

## Technologies

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests

