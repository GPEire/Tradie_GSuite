/**
 * Project Assignment Dialog Component
 * TASK-030: Manual project assignment UI
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Autocomplete,
  Box,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Close as CloseIcon,
  Folder as FolderIcon,
  LocationOn as LocationOnIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';
import { useProjectStore } from '../store/projectStore';

interface ProjectAssignmentDialogProps {
  open: boolean;
  onClose: () => void;
  emailId: string;
  emailSubject?: string;
  emailFrom?: string;
  currentProjectId?: string;
  onAssigned?: (projectId: string) => void;
  onRemoved?: () => void;
}

export const ProjectAssignmentDialog: React.FC<ProjectAssignmentDialogProps> = ({
  open,
  onClose,
  emailId,
  emailSubject,
  emailFrom,
  currentProjectId,
  onAssigned,
  onRemoved,
}) => {
  const { projects, loadProjects } = useProjectStore();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(currentProjectId || null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      loadProjects();
      setSelectedProjectId(currentProjectId || null);
      setError(null);
      setSuccess(null);
    }
  }, [open, currentProjectId, loadProjects]);

  const handleAssign = async () => {
    if (!selectedProjectId) {
      setError('Please select a project');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.addEmailToProject(selectedProjectId, emailId);
      setSuccess('Email assigned to project successfully');
      
      // Record correction if this is a change from original assignment
      if (currentProjectId && currentProjectId !== selectedProjectId) {
        await apiClient.recordCorrection({
          correction_type: 'project_assignment',
          original_result: { project_id: currentProjectId },
          corrected_result: { project_id: selectedProjectId },
          email_id: emailId,
          project_id: selectedProjectId,
          correction_reason: 'Manual reassignment',
        });
      }

      if (onAssigned) {
        onAssigned(selectedProjectId);
      }

      // Close after short delay
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to assign email to project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemove = async () => {
    if (!currentProjectId) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // TODO: Implement remove email from project endpoint
      // For now, we'll use a placeholder
      await apiClient.removeEmailFromProject(currentProjectId, emailId);
      setSuccess('Email removed from project');

      // Record correction
      await apiClient.recordCorrection({
        correction_type: 'project_assignment',
        original_result: { project_id: currentProjectId },
        corrected_result: { project_id: null },
        email_id: emailId,
        project_id: currentProjectId,
        correction_reason: 'Email removed from project',
      });

      if (onRemoved) {
        onRemoved();
      }

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to remove email from project');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredProjects = projects.filter((project) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      project.project_name.toLowerCase().includes(query) ||
      project.address?.toLowerCase().includes(query) ||
      project.client_name?.toLowerCase().includes(query)
    );
  });

  const selectedProject = projects.find((p) => p.project_id === selectedProjectId);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Assign to Project</Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        {emailSubject && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary">
              Email:
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              {emailSubject}
            </Typography>
            {emailFrom && (
              <Typography variant="caption" color="text.secondary">
                From: {emailFrom}
              </Typography>
            )}
          </Box>
        )}

        {currentProjectId && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Currently assigned to: {selectedProject?.project_name || currentProjectId}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Autocomplete
          options={filteredProjects}
          getOptionLabel={(option) => option.project_name}
          value={selectedProject || null}
          onChange={(_, newValue) => {
            setSelectedProjectId(newValue?.project_id || null);
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Search projects"
              placeholder="Type to search..."
              variant="outlined"
              fullWidth
              InputProps={{
                ...params.InputProps,
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          )}
          renderOption={(props, option) => (
            <Box component="li" {...props}>
              <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <FolderIcon fontSize="small" color="action" />
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {option.project_name}
                  </Typography>
                  {option.status !== 'active' && (
                    <Chip label={option.status} size="small" />
                  )}
                </Box>
                {option.address && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 3 }}>
                    <LocationOnIcon fontSize="inherit" sx={{ fontSize: 12 }} />
                    <Typography variant="caption" color="text.secondary">
                      {option.address}
                    </Typography>
                  </Box>
                )}
                {option.client_name && (
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 3 }}>
                    Client: {option.client_name}
                  </Typography>
                )}
              </Box>
            </Box>
          )}
          loading={isLoading}
          noOptionsText="No projects found"
        />

        {selectedProject && (
          <Box sx={{ mt: 2, p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Selected Project:
            </Typography>
            <Typography variant="body2">{selectedProject.project_name}</Typography>
            {selectedProject.address && (
              <Typography variant="caption" color="text.secondary" display="block">
                {selectedProject.address}
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary" display="block">
              {selectedProject.email_count || 0} emails in project
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        {currentProjectId && (
          <Button
            onClick={handleRemove}
            color="error"
            disabled={isLoading}
          >
            Remove from Project
          </Button>
        )}
        <Button onClick={onClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleAssign}
          variant="contained"
          disabled={!selectedProjectId || isLoading}
        >
          {isLoading ? <CircularProgress size={24} /> : 'Assign'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

