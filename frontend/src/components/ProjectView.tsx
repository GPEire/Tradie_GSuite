/**
 * Project View Component
 * Main container for project details, emails, attachments, and contacts
 */

import React, { useState } from 'react';
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
} from '@mui/icons-material';
import { ProjectEmailView } from './ProjectEmailView';
import { AttachmentManagement } from './AttachmentManagement';
import { ClientContactView } from './ClientContactView';

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

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', px: 2 }}>
        <Typography variant="h6" sx={{ flex: 1, py: 1 }}>
          Project Details
        </Typography>
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
    </Paper>
  );
};

