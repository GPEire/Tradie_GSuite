/**
 * Integration Settings Component
 * TASK-036: Build integration settings UI
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControlLabel,
  Switch,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  DriveFolderUpload as DriveIcon,
  ContactMail as ContactsIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';

interface IntegrationConfig {
  google_drive_enabled: boolean;
  google_contacts_enabled: boolean;
  calendar_enabled: boolean;
  drive_auto_upload: boolean;
  contacts_auto_sync: boolean;
}

export const IntegrationSettings: React.FC = () => {
  const [config, setConfig] = useState<IntegrationConfig>({
    google_drive_enabled: false,
    google_contacts_enabled: false,
    calendar_enabled: false,
    drive_auto_upload: false,
    contacts_auto_sync: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Replace with actual endpoint when backend implements it
      const data = await apiClient.getIntegrationSettings();
      setConfig(data);
    } catch (err: any) {
      // If endpoint doesn't exist yet, use defaults
      setConfig({
        google_drive_enabled: false,
        google_contacts_enabled: false,
        calendar_enabled: false,
        drive_auto_upload: false,
        contacts_auto_sync: false,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.updateIntegrationSettings(config);
      setSuccess('Settings saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ padding: 3 }}>
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

      {/* Google Drive Integration */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <DriveIcon />
          <Typography variant="h6">Google Drive Integration</Typography>
        </Box>
        <FormControlLabel
          control={
            <Switch
              checked={config.google_drive_enabled}
              onChange={(e) => {
                setConfig({
                  ...config,
                  google_drive_enabled: e.target.checked,
                  drive_auto_upload: e.target.checked ? config.drive_auto_upload : false,
                });
              }}
            />
          }
          label="Enable Google Drive Integration"
        />
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1, ml: 4 }}>
          Upload email attachments to Google Drive and organize by project
        </Typography>

        {config.google_drive_enabled && (
          <Box sx={{ mt: 2, ml: 4 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.drive_auto_upload}
                  onChange={(e) =>
                    setConfig({ ...config, drive_auto_upload: e.target.checked })
                  }
                />
              }
              label="Automatically upload attachments to Drive"
            />
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              Attachments will be automatically uploaded and organized by project
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Google Contacts Integration */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <ContactsIcon />
          <Typography variant="h6">Google Contacts Integration</Typography>
        </Box>
        <FormControlLabel
          control={
            <Switch
              checked={config.google_contacts_enabled}
              onChange={(e) => {
                setConfig({
                  ...config,
                  google_contacts_enabled: e.target.checked,
                  contacts_auto_sync: e.target.checked ? config.contacts_auto_sync : false,
                });
              }}
            />
          }
          label="Enable Google Contacts Sync"
        />
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1, ml: 4 }}>
          Sync extracted client contacts to Google Contacts
        </Typography>

        {config.google_contacts_enabled && (
          <Box sx={{ mt: 2, ml: 4 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.contacts_auto_sync}
                  onChange={(e) =>
                    setConfig({ ...config, contacts_auto_sync: e.target.checked })
                  }
                />
              }
              label="Automatically sync contacts"
            />
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              New contacts will be automatically added to Google Contacts
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Calendar Integration */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <CalendarIcon />
          <Typography variant="h6">Calendar Integration</Typography>
        </Box>
        <FormControlLabel
          control={
            <Switch
              checked={config.calendar_enabled}
              onChange={(e) =>
                setConfig({ ...config, calendar_enabled: e.target.checked })
              }
            />
          }
          label="Enable Calendar Integration"
        />
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1, ml: 4 }}>
          Create calendar events from project emails (future feature)
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          Calendar integration is planned for a future release
        </Alert>
      </Paper>

      {/* External CRM (Future) */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          External CRM Export
        </Typography>
        <Alert severity="info">
          External CRM export functionality is planned for a future release. This will allow
          exporting project data to popular CRM systems.
        </Alert>
      </Paper>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

