/**
 * Sidebar Entry Point
 * React component mounted in Gmail sidebar
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { Sidebar } from './components/Sidebar';

// Create Material-UI theme with Gmail-like styling
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1a73e8', // Gmail blue
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Google Sans", Roboto, Arial, sans-serif',
    fontSize: 14,
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderLeft: '1px solid #dadce0',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
          },
        },
      },
    },
  },
});

// Dark mode theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#8ab4f8',
    },
    background: {
      default: '#202124',
      paper: '#202124',
    },
  },
  typography: {
    fontFamily: '"Google Sans", Roboto, Arial, sans-serif',
    fontSize: 14,
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderLeft: '1px solid #5f6368',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
          },
        },
      },
    },
  },
});

// Check for dark mode preference
const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
const activeTheme = prefersDarkMode ? darkTheme : theme;

// Mount sidebar component
const rootElement = document.getElementById('sidebar-root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <ThemeProvider theme={activeTheme}>
        <CssBaseline />
        <Sidebar />
      </ThemeProvider>
    </React.StrictMode>
  );
} else {
  console.error('Sidebar root element not found');
}

