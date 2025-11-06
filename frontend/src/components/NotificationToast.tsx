/**
 * Notification Toast Component
 * TASK-033: Non-intrusive toast notifications
 */

import React, { useEffect } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Box,
  Typography,
  Button,
} from '@mui/material';
import {
  Close as CloseIcon,
  Email as EmailIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';
import { useNotificationStore, Notification } from '../store/notificationStore';

interface NotificationToastProps {
  maxNotifications?: number;
}

export const NotificationToast: React.FC<NotificationToastProps> = ({
  maxNotifications = 3,
}) => {
  const { notifications, removeNotification, markAsRead } = useNotificationStore();
  
  // Get unread notifications only, sorted by timestamp (newest first)
  const unreadNotifications = notifications
    .filter((n) => !n.read)
    .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    .slice(0, maxNotifications);

  const currentNotification = unreadNotifications[0];

  const handleClose = (notification: Notification) => {
    markAsRead(notification.id);
    removeNotification(notification.id);
  };

  const handleAction = (notification: Notification) => {
    if (notification.actionUrl) {
      window.open(notification.actionUrl, '_blank');
    }
    handleClose(notification);
  };

  if (!currentNotification) {
    return null;
  }

  const getActionButton = () => {
    if (currentNotification.actionUrl && currentNotification.actionLabel) {
      return (
        <Button
          size="small"
          onClick={() => handleAction(currentNotification)}
          sx={{ ml: 2 }}
        >
          {currentNotification.actionLabel}
        </Button>
      );
    }
    return null;
  };

  return (
    <Snackbar
      open={true}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      autoHideDuration={currentNotification.type === 'error' ? 10000 : 5000}
      onClose={() => handleClose(currentNotification)}
      sx={{ mt: 8 }}
    >
      <Alert
        severity={currentNotification.type}
        onClose={() => handleClose(currentNotification)}
        icon={
          currentNotification.category === 'new_project_email' ? (
            <EmailIcon />
          ) : currentNotification.category === 'low_confidence' ||
            currentNotification.category === 'multi_project' ? (
            <FolderIcon />
          ) : undefined
        }
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getActionButton()}
            <IconButton
              size="small"
              onClick={() => handleClose(currentNotification)}
              color="inherit"
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        }
        sx={{ minWidth: 300, maxWidth: 400 }}
      >
        <AlertTitle>{currentNotification.title}</AlertTitle>
        <Typography variant="body2">{currentNotification.message}</Typography>
      </Alert>
    </Snackbar>
  );
};

