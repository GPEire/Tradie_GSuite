/**
 * Gmail Sidebar Component
 * Main sidebar panel for displaying projects
 */

import React, { useEffect } from 'react';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemText, 
  ListItemIcon,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Badge,
} from '@mui/material';
import {
  Search as SearchIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Folder as FolderIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useProjectStore } from '../store/projectStore';
import { ProjectListItem } from './ProjectListItem';

interface SidebarProps {
  width?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ width = 320 }) => {
  const {
    projects,
    selectedProjectId,
    searchQuery,
    filterStatus,
    isLoading,
    error,
    isCollapsed,
    loadProjects,
    setSearchQuery,
    toggleCollapse,
    refreshProjects,
    selectProject,
  } = useProjectStore();

  useEffect(() => {
    loadProjects('active');
  }, [loadProjects]);

  // Filter projects based on search query
  const filteredProjects = projects.filter((project) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        project.project_name.toLowerCase().includes(query) ||
        project.address?.toLowerCase().includes(query) ||
        project.client_name?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  // Sort projects by last email date (most recent first)
  const sortedProjects = [...filteredProjects].sort((a, b) => {
    const dateA = a.last_email_at ? new Date(a.last_email_at).getTime() : 0;
    const dateB = b.last_email_at ? new Date(b.last_email_at).getTime() : 0;
    return dateB - dateA;
  });

  const handleRefresh = () => {
    refreshProjects();
  };

  if (isCollapsed) {
    return (
      <Box
        sx={{
          position: 'fixed',
          right: 0,
          top: 0,
          height: '100vh',
          width: 48,
          backgroundColor: 'background.paper',
          borderLeft: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          paddingTop: 2,
          zIndex: 1300,
        }}
      >
        <IconButton onClick={toggleCollapse} size="small">
          <ChevronLeftIcon />
        </IconButton>
      </Box>
    );
  }

  return (
    <Drawer
      variant="persistent"
      anchor="right"
      open={!isCollapsed}
      sx={{
        width: width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: width,
          boxSizing: 'border-box',
          position: 'fixed',
          right: 0,
          top: 0,
          height: '100vh',
          zIndex: 1300,
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          backgroundColor: 'background.paper',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            padding: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
            Projects
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={handleRefresh} disabled={isLoading}>
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Collapse">
              <IconButton
                size="small"
                onClick={() => {
                  toggleCollapse();
                  // Notify content script
                  if (window.parent) {
                    window.parent.postMessage({
                      type: isCollapsed ? 'SIDEBAR_EXPANDED' : 'SIDEBAR_COLLAPSED'
                    }, '*');
                  }
                }}
              >
                <ChevronRightIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Search */}
        <Box sx={{ padding: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Error Alert */}
        {error && (
          <Box sx={{ padding: 2 }}>
            <Alert severity="error" onClose={() => {}}>
              {error}
            </Alert>
          </Box>
        )}

        {/* Projects List */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            padding: 1,
          }}
        >
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
              <CircularProgress size={32} />
            </Box>
          ) : sortedProjects.length === 0 ? (
            <Box sx={{ padding: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {searchQuery ? 'No projects found' : 'No projects yet'}
              </Typography>
            </Box>
          ) : (
            <List dense>
              {sortedProjects.map((project) => (
                <ProjectListItem
                  key={project.project_id}
                  project={project}
                  isSelected={selectedProjectId === project.project_id}
                  onClick={() => {
                    selectProject(project.project_id);
                    // Notify content script
                    if (window.parent) {
                      window.parent.postMessage({
                        type: 'SELECT_PROJECT',
                        data: { projectId: project.project_id }
                      }, '*');
                    }
                  }}
                />
              ))}
            </List>
          )}
        </Box>

        {/* Footer */}
        <Box
          sx={{
            padding: 1.5,
            borderTop: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'background.default',
          }}
        >
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            {sortedProjects.length} project{sortedProjects.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

