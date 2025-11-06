/**
 * Project Email View Component
 * TASK-026: Display chronological email list for a project
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Divider,
  Paper,
} from '@mui/material';
import {
  Email as EmailIcon,
  AttachFile as AttachFileIcon,
  MarkEmailRead as MarkEmailReadIcon,
  MarkEmailUnread as MarkEmailUnreadIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { formatDistanceToNow, format } from 'date-fns';
import { apiClient } from '../services/api';
import { ProjectAssignmentDialog } from './ProjectAssignmentDialog';
import { Menu, MenuItem } from '@mui/material';
import { NotificationService } from '../services/notificationService';
import { NotificationService } from '../services/notificationService';

interface EmailMetadata {
  id: string;
  thread_id: string;
  subject: string;
  snippet: string;
  from_address: {
    name: string;
    email: string;
  };
  to_addresses: Array<{ name: string; email: string }>;
  cc_addresses: Array<{ name: string; email: string }>;
  date?: string;
  internal_date?: string;
  label_ids: string[];
  size_estimate: number;
}

interface ProjectEmailViewProps {
  projectId: string;
  onEmailClick?: (emailId: string) => void;
}

interface EmailMenuItemState {
  anchorEl: HTMLElement | null;
  emailId: string | null;
  emailSubject: string | null;
  emailFrom: string | null;
}

export const ProjectEmailView: React.FC<ProjectEmailViewProps> = ({
  projectId,
  onEmailClick,
}) => {
  const [emails, setEmails] = useState<EmailMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assignmentDialogOpen, setAssignmentDialogOpen] = useState(false);
  const [menuState, setMenuState] = useState<EmailMenuItemState>({
    anchorEl: null,
    emailId: null,
    emailSubject: null,
    emailFrom: null,
  });

  useEffect(() => {
    loadEmails();
  }, [projectId]);

  const loadEmails = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Replace with actual endpoint when backend implements it
      // For now, we'll fetch emails using Gmail API with project filter
      const data = await apiClient.getProjectEmails(projectId);
      const loadedEmails = Array.isArray(data) ? data : data.emails || [];
      setEmails(loadedEmails);
      
      // Notify about new emails if we detect them
      // This would be better handled by watching for changes
      if (loadedEmails.length > 0) {
        // Get project name from store or API
        // NotificationService.notifyNewProjectEmail(...);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load emails');
      console.error('Error loading project emails:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatEmailDate = (dateString?: string) => {
    if (!dateString) return 'Unknown date';
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
      
      if (diffInHours < 24) {
        return formatDistanceToNow(date, { addSuffix: true });
      } else if (diffInHours < 168) { // Less than a week
        return format(date, 'EEEE, h:mm a');
      } else {
        return format(date, 'MMM d, yyyy');
      }
    } catch {
      return 'Invalid date';
    }
  };

  const isUnread = (labelIds: string[]) => {
    return !labelIds.includes('UNREAD');
  };

  const hasAttachments = (email: EmailMetadata) => {
    // Check if email has attachments (this would come from the backend)
    // For now, we'll check label_ids or metadata
    return false; // Placeholder
  };

  const handleEmailClick = (emailId: string) => {
    if (onEmailClick) {
      onEmailClick(emailId);
    } else {
      // Default: Open email in Gmail
      window.open(`https://mail.google.com/mail/u/0/#inbox/${emailId}`, '_blank');
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, email: EmailMetadata) => {
    setMenuState({
      anchorEl: event.currentTarget,
      emailId: email.id,
      emailSubject: email.subject,
      emailFrom: email.from_address.email,
    });
  };

  const handleMenuClose = () => {
    setMenuState({
      anchorEl: null,
      emailId: null,
      emailSubject: null,
      emailFrom: null,
    });
  };

  const handleAssignToProject = () => {
    handleMenuClose();
    setAssignmentDialogOpen(true);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ padding: 2 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (emails.length === 0) {
    return (
      <Box sx={{ padding: 4, textAlign: 'center' }}>
        <EmailIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          No emails found for this project
        </Typography>
      </Box>
    );
  }

  // Sort emails by date (most recent first)
  const sortedEmails = [...emails].sort((a, b) => {
    const dateA = a.date ? new Date(a.date).getTime() : 0;
    const dateB = b.date ? new Date(b.date).getTime() : 0;
    return dateB - dateA;
  });

  return (
    <Paper sx={{ height: '100%', overflow: 'auto' }}>
      <Box sx={{ padding: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" component="h2">
          Project Emails ({emails.length})
        </Typography>
      </Box>
      <List dense={false}>
        {sortedEmails.map((email, index) => (
          <React.Fragment key={email.id}>
            <ListItem
              button
              onClick={() => handleEmailClick(email.id)}
              sx={{
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon>
                {isUnread(email.label_ids) ? (
                  <MarkEmailUnreadIcon color="primary" />
                ) : (
                  <MarkEmailReadIcon color="action" />
                )}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography
                      variant="subtitle2"
                      component="span"
                      sx={{
                        fontWeight: isUnread(email.label_ids) ? 600 : 400,
                        flex: 1,
                      }}
                    >
                      {email.subject || '(No subject)'}
                    </Typography>
                    {hasAttachments(email) && (
                      <Tooltip title="Has attachments">
                        <AttachFileIcon fontSize="small" color="action" />
                      </Tooltip>
                    )}
                  </Box>
                }
                secondary={
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <PersonIcon fontSize="inherit" sx={{ fontSize: 14, mr: 0.5 }} />
                      <Typography variant="caption" color="text.secondary">
                        {email.from_address.name || email.from_address.email}
                      </Typography>
                      {email.to_addresses.length > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          • {email.to_addresses.length} recipient{email.to_addresses.length !== 1 ? 's' : ''}
                        </Typography>
                      )}
                    </Box>
                    {email.snippet && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          mb: 0.5,
                        }}
                      >
                        {email.snippet}
                      </Typography>
                    )}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ScheduleIcon fontSize="inherit" sx={{ fontSize: 12 }} />
                      <Typography variant="caption" color="text.secondary">
                        {formatEmailDate(email.date || email.internal_date)}
                      </Typography>
                    </Box>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Tooltip title={formatEmailDate(email.date || email.internal_date)}>
                    <IconButton edge="end" size="small">
                      <ScheduleIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="More options">
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMenuOpen(e, email);
                      }}
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItemSecondaryAction>
            </ListItem>
            {index < sortedEmails.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>

      {/* Email Menu */}
      <Menu
        anchorEl={menuState.anchorEl}
        open={Boolean(menuState.anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleAssignToProject}>
          Assign to Project...
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          Remove from Project
        </MenuItem>
      </Menu>

      {/* Assignment Dialog */}
      <ProjectAssignmentDialog
        open={assignmentDialogOpen}
        onClose={() => setAssignmentDialogOpen(false)}
        emailId={menuState.emailId || ''}
        emailSubject={menuState.emailSubject || undefined}
        emailFrom={menuState.emailFrom || undefined}
        currentProjectId={projectId}
        onAssigned={() => {
          loadEmails();
        }}
        onRemoved={() => {
          loadEmails();
        }}
      />
    </Paper>
  );
};

