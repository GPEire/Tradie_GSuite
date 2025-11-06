/**
 * Attachment Management Component
 * TASK-028: Display and manage attachments for a project
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
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Paper,
  Grid,
} from '@mui/material';
import {
  AttachFile as AttachFileIcon,
  Description as DescriptionIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  TableChart as TableChartIcon,
  Archive as ArchiveIcon,
  GetApp as DownloadIcon,
  OpenInNew as OpenIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '../services/api';

interface Attachment {
  id: number;
  attachment_id: string;
  filename: string;
  mime_type: string;
  size: number;
  file_extension?: string;
  file_type_category?: string;
  project_id?: string;
  email_id?: string;
  created_at: string;
  drive_file_id?: string;
  drive_url?: string;
  is_uploaded_to_drive: boolean;
}

interface AttachmentManagementProps {
  projectId: string;
}

export const AttachmentManagement: React.FC<AttachmentManagementProps> = ({
  projectId,
}) => {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAttachments();
  }, [projectId]);

  const loadAttachments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getProjectAttachments(projectId);
      setAttachments(Array.isArray(data) ? data : data.attachments || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load attachments');
      console.error('Error loading attachments:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getFileIcon = (mimeType: string, category?: string) => {
    if (category) {
      switch (category) {
        case 'image':
          return <ImageIcon />;
        case 'document':
          return <DescriptionIcon />;
        case 'spreadsheet':
          return <TableChartIcon />;
        case 'archive':
          return <ArchiveIcon />;
        default:
          return <AttachFileIcon />;
      }
    }

    if (mimeType.includes('pdf')) {
      return <PdfIcon />;
    }
    if (mimeType.startsWith('image/')) {
      return <ImageIcon />;
    }
    if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) {
      return <TableChartIcon />;
    }
    return <AttachFileIcon />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleDownload = async (attachment: Attachment) => {
    if (attachment.drive_url) {
      window.open(attachment.drive_url, '_blank');
    } else {
      // TODO: Implement download from Gmail API
      console.log('Download attachment:', attachment);
    }
  };

  const handleOpenInDrive = (attachment: Attachment) => {
    if (attachment.drive_url) {
      window.open(attachment.drive_url, '_blank');
    }
  };

  // Group attachments by category
  const groupedAttachments = attachments.reduce((acc, attachment) => {
    const category = attachment.file_type_category || 'other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(attachment);
    return acc;
  }, {} as Record<string, Attachment[]>);

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

  if (attachments.length === 0) {
    return (
      <Box sx={{ padding: 4, textAlign: 'center' }}>
        <AttachFileIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          No attachments found for this project
        </Typography>
      </Box>
    );
  }

  const totalSize = attachments.reduce((sum, att) => sum + att.size, 0);

  return (
    <Paper sx={{ height: '100%', overflow: 'auto' }}>
      <Box sx={{ padding: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6" component="h2">
              Attachments ({attachments.length})
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total size: {formatFileSize(totalSize)}
            </Typography>
          </Box>
        </Box>
      </Box>

      <List>
        {Object.entries(groupedAttachments).map(([category, categoryAttachments], categoryIndex) => (
          <React.Fragment key={category}>
            {categoryIndex > 0 && <Divider />}
            <Box sx={{ padding: 2, backgroundColor: 'background.default' }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                {category} ({categoryAttachments.length})
              </Typography>
            </Box>
            {categoryAttachments.map((attachment, index) => (
              <React.Fragment key={attachment.id}>
                <ListItem>
                  <ListItemIcon>
                    {getFileIcon(attachment.mime_type, attachment.file_type_category)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" noWrap sx={{ flex: 1 }}>
                          {attachment.filename}
                        </Typography>
                        {attachment.is_uploaded_to_drive && (
                          <Tooltip title="Uploaded to Google Drive">
                            <Chip
                              label="Drive"
                              size="small"
                              icon={<CloudUploadIcon />}
                              color="success"
                              variant="outlined"
                            />
                          </Tooltip>
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          {formatFileSize(attachment.size)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          •
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatDistanceToNow(new Date(attachment.created_at), { addSuffix: true })}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {attachment.drive_url && (
                        <Tooltip title="Open in Drive">
                          <IconButton size="small" onClick={() => handleOpenInDrive(attachment)}>
                            <OpenIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Download">
                        <IconButton size="small" onClick={() => handleDownload(attachment)}>
                          <DownloadIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < categoryAttachments.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            ))}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

