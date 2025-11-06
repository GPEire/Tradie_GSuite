/**
 * Project Naming Rules Configuration Component
 * TASK-035: Implement project naming rules configuration
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  FormControl,
  FormLabel,
  FormHelperText,
  Chip,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';

interface ProjectNamingRule {
  id?: string;
  pattern: string;
  description: string;
  enabled: boolean;
  category?: string;
}

interface ProjectNamingConfig {
  rules: ProjectNamingRule[];
  label_format?: string;
  auto_create_labels: boolean;
}

export const ProjectNamingRules: React.FC = () => {
  const [config, setConfig] = useState<ProjectNamingConfig>({
    rules: [],
    label_format: 'project_{name}',
    auto_create_labels: true,
  });
  const [newRule, setNewRule] = useState<Partial<ProjectNamingRule>>({
    pattern: '',
    description: '',
    enabled: true,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [patternError, setPatternError] = useState<string | null>(null);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Replace with actual endpoint when backend implements it
      // For now, use placeholder
      const data = await apiClient.getProjectNamingConfig();
      setConfig(data);
    } catch (err: any) {
      // If endpoint doesn't exist yet, use defaults
      setConfig({
        rules: [],
        label_format: 'project_{name}',
        auto_create_labels: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const validatePattern = (pattern: string): boolean => {
    try {
      new RegExp(pattern);
      return true;
    } catch {
      return false;
    }
  };

  const handleAddRule = () => {
    if (!newRule.pattern || !newRule.description) {
      setPatternError('Pattern and description are required');
      return;
    }

    if (!validatePattern(newRule.pattern)) {
      setPatternError('Invalid regex pattern');
      return;
    }

    setConfig({
      ...config,
      rules: [
        ...config.rules,
        {
          id: `rule-${Date.now()}`,
          pattern: newRule.pattern,
          description: newRule.description,
          enabled: newRule.enabled ?? true,
          category: newRule.category,
        },
      ],
    });

    setNewRule({ pattern: '', description: '', enabled: true });
    setPatternError(null);
  };

  const handleRemoveRule = (id: string) => {
    setConfig({
      ...config,
      rules: config.rules.filter((r) => r.id !== id),
    });
  };

  const handleToggleRule = (id: string) => {
    setConfig({
      ...config,
      rules: config.rules.map((r) =>
        r.id === id ? { ...r, enabled: !r.enabled } : r
      ),
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.updateProjectNamingConfig(config);
      setSuccess('Configuration saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save configuration');
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

      {/* Label Format */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Label Format
        </Typography>
        <TextField
          fullWidth
          label="Label Format Pattern"
          value={config.label_format}
          onChange={(e) => setConfig({ ...config, label_format: e.target.value })}
          helperText="Use {name} for project name, {id} for project ID"
          sx={{ mb: 2 }}
        />
        <FormControlLabel
          control={
            <Switch
              checked={config.auto_create_labels}
              onChange={(e) =>
                setConfig({ ...config, auto_create_labels: e.target.checked })
              }
            />
          }
          label="Automatically create Gmail labels for projects"
        />
      </Paper>

      {/* Naming Rules */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Project Naming Rules
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Define regex patterns to identify project names from email content
        </Typography>

        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            label="Regex Pattern"
            value={newRule.pattern}
            onChange={(e) => {
              setNewRule({ ...newRule, pattern: e.target.value });
              if (patternError) setPatternError(null);
            }}
            error={!!patternError}
            helperText={patternError || 'Example: Project: ([A-Za-z0-9 ]+)'}
            sx={{ mb: 1 }}
          />
          <TextField
            fullWidth
            label="Description"
            value={newRule.description}
            onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
            helperText="Describe what this pattern matches"
            sx={{ mb: 1 }}
          />
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleAddRule}
            disabled={!newRule.pattern || !newRule.description}
          >
            Add Rule
          </Button>
        </Box>

        <Divider sx={{ my: 2 }} />

        {config.rules.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
            No naming rules configured. Add rules to help identify project names.
          </Typography>
        ) : (
          <Box>
            {config.rules.map((rule) => (
              <Paper
                key={rule.id}
                sx={{
                  p: 2,
                  mb: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: rule.enabled ? 'background.paper' : 'action.disabledBackground',
                }}
              >
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chip
                      label={rule.enabled ? 'Enabled' : 'Disabled'}
                      size="small"
                      color={rule.enabled ? 'success' : 'default'}
                    />
                    {rule.category && (
                      <Chip label={rule.category} size="small" variant="outlined" />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 0.5 }}>
                    {rule.pattern}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {rule.description}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    onClick={() => rule.id && handleToggleRule(rule.id)}
                  >
                    {rule.enabled ? 'Disable' : 'Enable'}
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => rule.id && handleRemoveRule(rule.id)}
                  >
                    Remove
                  </Button>
                </Box>
              </Paper>
            ))}
          </Box>
        )}
      </Paper>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
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
  );
};

