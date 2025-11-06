/**
 * Project View Component
 * Main container for project details, emails, attachments, and contacts
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Email as EmailIcon,
  AttachFile as AttachFileIcon,
  Person as PersonIcon,
  Dashboard as DashboardIcon,
  Close as CloseIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { ProjectEmailView } from './ProjectEmailView';
import { AttachmentManagement } from './AttachmentManagement';
import { ClientContactView } from './ClientContactView';
import { ProjectManagementDialog } from './ProjectManagementDialog';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && <Box sx={{ height: '100%', overflow: 'auto' }}>{children}</Box>}
    </div>
  );
}

interface ProjectViewProps {
  projectId: string;
  onClose?: () => void;
}

export const ProjectView: React.FC<ProjectViewProps> = ({
  projectId,
  onClose,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [managementDialogOpen, setManagementDialogOpen] = useState(false);
  const [projectName, setProjectName] = useState('');

  useEffect(() => {
    // Load project name
    const loadProject = async () => {
      try {
        const project = await apiClient.getProject(projectId);
        setProjectName(project.project_name || projectId);
      } catch (error) {
        console.error('Error loading project:', error);
      }
    };
    loadProject();
  }, [projectId]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', px: 2 }}>
        <Typography variant="h6" sx={{ flex: 1, py: 1 }}>
          {projectName || 'Project Details'}
        </Typography>
        <Tooltip title="Manage Project">
          <IconButton size="small" onClick={() => setManagementDialogOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Tooltip>
        {onClose && (
          <Tooltip title="Close">
            <IconButton size="small" onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>
      <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tab icon={<EmailIcon />} label="Emails" iconPosition="start" />
        <Tab icon={<AttachFileIcon />} label="Attachments" iconPosition="start" />
        <Tab icon={<PersonIcon />} label="Contacts" iconPosition="start" />
      </Tabs>
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <TabPanel value={tabValue} index={0}>
          <ProjectEmailView projectId={projectId} />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <AttachmentManagement projectId={projectId} />
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <ClientContactView projectId={projectId} />
        </TabPanel>
      </Box>

      {/* Project Management Dialog */}
      <ProjectManagementDialog
        open={managementDialogOpen}
        onClose={() => setManagementDialogOpen(false)}
        projectId={projectId}
        projectName={projectName}
        onUpdated={() => {
          // Reload project name
          apiClient.getProject(projectId).then((project) => {
            setProjectName(project.project_name || projectId);
          });
        }}
      />
    </Paper>
  );
};

