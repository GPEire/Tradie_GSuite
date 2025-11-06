/**
 * Project List Item Component
 * Individual project item in the sidebar list
 */

import React from 'react';
import {
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Chip,
  Box,
  Typography,
} from '@mui/material';
import {
  Folder as FolderIcon,
  Warning as WarningIcon,
  LocationOn as LocationIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

interface Project {
  id: number;
  project_id: string;
  project_name: string;
  address?: string;
  client_name?: string;
  project_type?: string;
  email_count: number;
  last_email_at?: string;
  status: string;
  needs_review: boolean;
}

interface ProjectListItemProps {
  project: Project;
  isSelected: boolean;
  onClick?: () => void;
}

export const ProjectListItem: React.FC<ProjectListItemProps> = ({
  project,
  isSelected,
  onClick,
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      // Default: Select project in store
      const { useProjectStore } = require('../store/projectStore');
      useProjectStore.getState().selectProject(project.project_id);
      
      // Notify parent window (for content script communication)
      if (window.parent) {
        window.parent.postMessage({
          type: 'SELECT_PROJECT',
          data: { projectId: project.project_id }
        }, '*');
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'completed':
        return 'default';
      case 'on_hold':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatLastEmail = (dateString?: string) => {
    if (!dateString) return 'No emails';
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={isSelected}
        onClick={handleClick}
        sx={{
          borderRadius: 1,
          marginBottom: 0.5,
          '&.Mui-selected': {
            backgroundColor: 'primary.light',
            '&:hover': {
              backgroundColor: 'primary.light',
            },
          },
        }}
      >
        <ListItemIcon sx={{ minWidth: 40 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            <FolderIcon fontSize="small" color={isSelected ? 'primary' : 'action'} />
            {project.needs_review && (
              <WarningIcon fontSize="small" color="warning" />
            )}
          </Box>
        </ListItemIcon>
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="subtitle2" component="span" noWrap sx={{ flex: 1 }}>
                {project.project_name}
              </Typography>
              {project.status !== 'active' && (
                <Chip
                  label={project.status}
                  size="small"
                  color={getStatusColor(project.status) as any}
                  sx={{ height: 20, fontSize: '0.65rem' }}
                />
              )}
            </Box>
          }
          secondary={
            <Box>
              {project.address && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.25 }}>
                  <LocationIcon fontSize="inherit" sx={{ fontSize: 12 }} />
                  <Typography variant="caption" color="text.secondary" noWrap>
                    {project.address}
                  </Typography>
                </Box>
              )}
              {project.client_name && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.25 }}>
                  <PersonIcon fontSize="inherit" sx={{ fontSize: 12 }} />
                  <Typography variant="caption" color="text.secondary" noWrap>
                    {project.client_name}
                  </Typography>
                </Box>
              )}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  {project.email_count} email{project.email_count !== 1 ? 's' : ''}
                </Typography>
                {project.last_email_at && (
                  <Typography variant="caption" color="text.secondary">
                    • {formatLastEmail(project.last_email_at)}
                  </Typography>
                )}
              </Box>
            </Box>
          }
        />
      </ListItemButton>
    </ListItem>
  );
};

