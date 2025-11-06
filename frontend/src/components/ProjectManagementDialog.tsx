/**
 * Project Management Dialog Component
 * TASK-031: Project management controls (rename, delete, merge, split)
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Autocomplete,
  Chip,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  MergeType as MergeIcon,
  CallSplit as SplitIcon,
  Close as CloseIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';
import { useProjectStore } from '../store/projectStore';

interface ProjectManagementDialogProps {
  open: boolean;
  onClose: () => void;
  projectId: string;
  projectName: string;
  onUpdated?: () => void;
}

export const ProjectManagementDialog: React.FC<ProjectManagementDialogProps> = ({
  open,
  onClose,
  projectId,
  projectName,
  onUpdated,
}) => {
  const { projects, loadProjects } = useProjectStore();
  const [tabValue, setTabValue] = useState(0);
  const [newName, setNewName] = useState(projectName);
  const [mergeTargetId, setMergeTargetId] = useState<string | null>(null);
  const [splitEmails, setSplitEmails] = useState<string[]>([]);
  const [newProjectName, setNewProjectName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleRename = async () => {
    if (!newName.trim()) {
      setError('Project name cannot be empty');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.updateProject(projectId, { project_name: newName });
      setSuccess('Project renamed successfully');

      // Record correction
      await apiClient.recordCorrection({
        correction_type: 'project_rename',
        original_result: { project_name: projectName },
        corrected_result: { project_name: newName },
        project_id: projectId,
        correction_reason: 'Manual rename',
      });

      if (onUpdated) {
        onUpdated();
      }
      loadProjects();

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to rename project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete project "${projectName}"? This action cannot be undone.`)) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.deleteProject(projectId);
      setSuccess('Project deleted successfully');

      if (onUpdated) {
        onUpdated();
      }
      loadProjects();

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to delete project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMerge = async () => {
    if (!mergeTargetId) {
      setError('Please select a target project to merge with');
      return;
    }

    if (mergeTargetId === projectId) {
      setError('Cannot merge project with itself');
      return;
    }

    if (!window.confirm(`Merge "${projectName}" into the selected project? All emails will be moved.`)) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.mergeProjects(projectId, mergeTargetId);
      setSuccess('Projects merged successfully');

      // Record correction
      await apiClient.recordCorrection({
        correction_type: 'project_merge',
        original_result: { project_id: projectId, project_name: projectName },
        corrected_result: { project_id: mergeTargetId },
        project_id: projectId,
        correction_reason: 'Manual merge',
      });

      if (onUpdated) {
        onUpdated();
      }
      loadProjects();

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to merge projects');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSplit = async () => {
    if (splitEmails.length === 0) {
      setError('Please select at least one email to split');
      return;
    }

    if (!newProjectName.trim()) {
      setError('Please enter a name for the new project');
      return;
    }

    if (!window.confirm(`Split ${splitEmails.length} email(s) into a new project "${newProjectName}"?`)) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.splitProject(projectId, splitEmails, newProjectName);
      setSuccess('Project split successfully');

      // Record correction
      await apiClient.recordCorrection({
        correction_type: 'project_split',
        original_result: { project_id: projectId, project_name: projectName },
        corrected_result: { new_project_name: newProjectName, email_ids: splitEmails },
        project_id: projectId,
        correction_reason: 'Manual split',
      });

      if (onUpdated) {
        onUpdated();
      }
      loadProjects();

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to split project');
    } finally {
      setIsLoading(false);
    }
  };

  const availableProjects = projects.filter((p) => p.project_id !== projectId);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Manage Project: {projectName}</Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ mb: 2 }}>
          <Tab icon={<EditIcon />} label="Rename" iconPosition="start" />
          <Tab icon={<MergeIcon />} label="Merge" iconPosition="start" />
          <Tab icon={<SplitIcon />} label="Split" iconPosition="start" />
          <Tab icon={<DeleteIcon />} label="Delete" iconPosition="start" />
        </Tabs>

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

        {/* Rename Tab */}
        {tabValue === 0 && (
          <Box>
            <TextField
              fullWidth
              label="Project Name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              variant="outlined"
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              onClick={handleRename}
              disabled={isLoading || !newName.trim() || newName === projectName}
              startIcon={<EditIcon />}
            >
              {isLoading ? 'Renaming...' : 'Rename Project'}
            </Button>
          </Box>
        )}

        {/* Merge Tab */}
        {tabValue === 1 && (
          <Box>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <WarningIcon sx={{ mr: 1 }} />
              Merging will move all emails from this project to the target project. This action cannot be undone.
            </Alert>
            <Autocomplete
              options={availableProjects}
              getOptionLabel={(option) => option.project_name}
              value={availableProjects.find((p) => p.project_id === mergeTargetId) || null}
              onChange={(_, newValue) => {
                setMergeTargetId(newValue?.project_id || null);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select target project to merge with"
                  variant="outlined"
                  fullWidth
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box>
                    <Typography variant="body2">{option.project_name}</Typography>
                    {option.address && (
                      <Typography variant="caption" color="text.secondary">
                        {option.address}
                      </Typography>
                    )}
                  </Box>
                </Box>
              )}
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleMerge}
              disabled={isLoading || !mergeTargetId}
              startIcon={<MergeIcon />}
            >
              {isLoading ? 'Merging...' : 'Merge Projects'}
            </Button>
          </Box>
        )}

        {/* Split Tab */}
        {tabValue === 2 && (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              Select emails to split into a new project. This will create a new project and move selected emails.
            </Alert>
            <TextField
              fullWidth
              label="New Project Name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              variant="outlined"
              sx={{ mb: 2 }}
            />
            {/* TODO: Implement email selection list for split */}
            <Typography variant="body2" color="text.secondary">
              Email selection UI will be implemented when backend endpoint is available.
            </Typography>
            <Button
              variant="contained"
              onClick={handleSplit}
              disabled={isLoading || splitEmails.length === 0 || !newProjectName.trim()}
              startIcon={<SplitIcon />}
              sx={{ mt: 2 }}
            >
              {isLoading ? 'Splitting...' : 'Split Project'}
            </Button>
          </Box>
        )}

        {/* Delete Tab */}
        {tabValue === 3 && (
          <Box>
            <Alert severity="error" sx={{ mb: 2 }}>
              <WarningIcon sx={{ mr: 1 }} />
              Deleting a project will remove all associations. This action cannot be undone.
            </Alert>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Are you sure you want to delete this project? All email associations will be removed.
            </Typography>
            <Button
              variant="contained"
              color="error"
              onClick={handleDelete}
              disabled={isLoading}
              startIcon={<DeleteIcon />}
            >
              {isLoading ? 'Deleting...' : 'Delete Project'}
            </Button>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

