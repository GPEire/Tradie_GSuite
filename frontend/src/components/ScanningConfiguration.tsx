/**
 * Scanning Configuration Component
 * TASK-034: Build scanning configuration UI
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  FormControlLabel,
  FormLabel,
  RadioGroup,
  Radio,
  Switch,
  TextField,
  Button,
  Chip,
  Autocomplete,
  Typography,
  Divider,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { apiClient } from '../services/api';

interface ScanConfiguration {
  id?: number;
  is_enabled: boolean;
  scan_frequency: string;
  included_labels?: string[];
  excluded_labels?: string[];
  excluded_senders?: string[];
  excluded_domains?: string[];
  scan_retroactive?: boolean;
  retroactive_date_start?: string;
  retroactive_date_end?: string;
}

interface GmailLabel {
  id: string;
  name: string;
}

export const ScanningConfiguration: React.FC = () => {
  const [config, setConfig] = useState<ScanConfiguration>({
    is_enabled: true,
    scan_frequency: 'realtime',
    scan_retroactive: false,
  });
  const [availableLabels, setAvailableLabels] = useState<GmailLabel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadConfiguration();
    loadLabels();
  }, []);

  const loadConfiguration = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getScanConfiguration();
      setConfig({
        is_enabled: data.is_enabled ?? true,
        scan_frequency: data.scan_frequency || 'realtime',
        included_labels: data.included_labels || [],
        excluded_labels: data.excluded_labels || [],
        excluded_senders: data.excluded_senders || [],
        excluded_domains: data.excluded_domains || [],
        scan_retroactive: false,
      });
    } catch (err: any) {
      setError(err.message || 'Failed to load configuration');
    } finally {
      setIsLoading(false);
    }
  };

  const loadLabels = async () => {
    try {
      const labels = await apiClient.getGmailLabels();
      setAvailableLabels(labels.map((l: any) => ({ id: l.id, name: l.name })));
    } catch (err) {
      console.error('Error loading labels:', err);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.updateScanConfiguration(config);
      setSuccess('Configuration saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSender = (sender: string) => {
    if (sender && !config.excluded_senders?.includes(sender)) {
      setConfig({
        ...config,
        excluded_senders: [...(config.excluded_senders || []), sender.trim()],
      });
    }
  };

  const handleRemoveSender = (sender: string) => {
    setConfig({
      ...config,
      excluded_senders: config.excluded_senders?.filter((s) => s !== sender) || [],
    });
  };

  const handleAddDomain = (domain: string) => {
    if (domain && !config.excluded_domains?.includes(domain)) {
      setConfig({
        ...config,
        excluded_domains: [...(config.excluded_domains || []), domain.trim()],
      });
    }
  };

  const handleRemoveDomain = (domain: string) => {
    setConfig({
      ...config,
      excluded_domains: config.excluded_domains?.filter((d) => d !== domain) || [],
    });
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
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

        {/* Enable/Disable Scanning */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={config.is_enabled}
                onChange={(e) => setConfig({ ...config, is_enabled: e.target.checked })}
              />
            }
            label="Enable Email Scanning"
          />
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
            Automatically scan and group emails by project
          </Typography>
        </Paper>

        {/* Scanning Frequency */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Scanning Frequency</FormLabel>
            <RadioGroup
              value={config.scan_frequency}
              onChange={(e) => setConfig({ ...config, scan_frequency: e.target.value })}
            >
              <FormControlLabel value="realtime" control={<Radio />} label="Real-time (immediate)" />
              <FormControlLabel value="hourly" control={<Radio />} label="Hourly" />
              <FormControlLabel value="daily" control={<Radio />} label="Daily" />
              <FormControlLabel value="weekly" control={<Radio />} label="Weekly" />
              <FormControlLabel value="manual" control={<Radio />} label="Manual only" />
            </RadioGroup>
          </FormControl>
        </Paper>

        {/* Label/Folder Selection */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Label/Folder Selection
          </Typography>
          <Autocomplete
            multiple
            options={availableLabels}
            getOptionLabel={(option) => option.name}
            value={availableLabels.filter((l) => config.included_labels?.includes(l.id))}
            onChange={(_, newValue) => {
              setConfig({
                ...config,
                included_labels: newValue.map((l) => l.id),
              });
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Include Labels"
                placeholder="Select labels to scan"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option.name}
                  {...getTagProps({ index })}
                  key={option.id}
                />
              ))
            }
            sx={{ mb: 2 }}
          />
          <Autocomplete
            multiple
            options={availableLabels}
            getOptionLabel={(option) => option.name}
            value={availableLabels.filter((l) => config.excluded_labels?.includes(l.id))}
            onChange={(_, newValue) => {
              setConfig({
                ...config,
                excluded_labels: newValue.map((l) => l.id),
              });
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Exclude Labels"
                placeholder="Select labels to exclude"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option.name}
                  {...getTagProps({ index })}
                  key={option.id}
                />
              ))
            }
          />
        </Paper>

        {/* Sender Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Excluded Senders
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="email@example.com"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const input = e.target as HTMLInputElement;
                  handleAddSender(input.value);
                  input.value = '';
                }
              }}
            />
            <Button
              variant="outlined"
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                if (input) {
                  handleAddSender(input.value);
                  input.value = '';
                }
              }}
            >
              Add
            </Button>
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {config.excluded_senders?.map((sender) => (
              <Chip
                key={sender}
                label={sender}
                onDelete={() => handleRemoveSender(sender)}
              />
            ))}
          </Box>
        </Paper>

        {/* Domain Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Excluded Domains
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="example.com"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const input = e.target as HTMLInputElement;
                  handleAddDomain(input.value);
                  input.value = '';
                }
              }}
            />
            <Button
              variant="outlined"
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                if (input) {
                  handleAddDomain(input.value);
                  input.value = '';
                }
              }}
            >
              Add
            </Button>
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {config.excluded_domains?.map((domain) => (
              <Chip
                key={domain}
                label={domain}
                onDelete={() => handleRemoveDomain(domain)}
              />
            ))}
          </Box>
        </Paper>

        {/* Retroactive Scanning */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={config.scan_retroactive || false}
                onChange={(e) => setConfig({ ...config, scan_retroactive: e.target.checked })}
              />
            }
            label="Enable Retroactive Scanning"
          />
          {config.scan_retroactive && (
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <DatePicker
                label="Start Date"
                value={config.retroactive_date_start ? new Date(config.retroactive_date_start) : null}
                onChange={(date) => {
                  setConfig({
                    ...config,
                    retroactive_date_start: date?.toISOString(),
                  });
                }}
                slotProps={{ textField: { fullWidth: true } }}
              />
              <DatePicker
                label="End Date"
                value={config.retroactive_date_end ? new Date(config.retroactive_date_end) : null}
                onChange={(date) => {
                  setConfig({
                    ...config,
                    retroactive_date_end: date?.toISOString(),
                  });
                }}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </Box>
          )}
        </Paper>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadConfiguration}
            disabled={isSaving}
          >
            Reset
          </Button>
          <Button
            variant="contained"
            startIcon={isSaving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Configuration'}
          </Button>
        </Box>
      </Box>
    </LocalizationProvider>
  );
};

