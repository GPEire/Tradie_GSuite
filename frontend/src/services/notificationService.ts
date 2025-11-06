/**
 * Notification Service
 * TASK-033: Service for creating and managing notifications
 */

import { useNotificationStore, NotificationCategory } from '../store/notificationStore';

export class NotificationService {
  /**
   * Create notification for new project email
   */
  static notifyNewProjectEmail(
    projectName: string,
    emailSubject: string,
    projectId: string,
    emailId: string
  ) {
    useNotificationStore.getState().addNotification({
      type: 'info',
      category: 'new_project_email',
      title: `New email in ${projectName}`,
      message: emailSubject,
      projectId,
      emailId,
      actionUrl: `https://mail.google.com/mail/u/0/#inbox/${emailId}`,
      actionLabel: 'View Email',
    });
  }

  /**
   * Create notification for low-confidence grouping
   */
  static notifyLowConfidence(
    projectName: string,
    confidence: number,
    projectId: string,
    emailId?: string
  ) {
    useNotificationStore.getState().addNotification({
      type: 'warning',
      category: 'low_confidence',
      title: `Low confidence grouping: ${projectName}`,
      message: `This email was grouped with ${Math.round(confidence * 100)}% confidence. Please review.`,
      projectId,
      emailId,
      actionUrl: emailId
        ? `https://mail.google.com/mail/u/0/#inbox/${emailId}`
        : undefined,
      actionLabel: emailId ? 'Review Email' : undefined,
    });
  }

  /**
   * Create notification for multi-project detection
   */
  static notifyMultiProject(
    emailSubject: string,
    projectNames: string[],
    emailId: string
  ) {
    useNotificationStore.getState().addNotification({
      type: 'warning',
      category: 'multi_project',
      title: 'Multiple projects detected',
      message: `Email "${emailSubject}" matches ${projectNames.length} projects: ${projectNames.join(', ')}`,
      emailId,
      actionUrl: `https://mail.google.com/mail/u/0/#inbox/${emailId}`,
      actionLabel: 'Review Email',
    });
  }

  /**
   * Create notification for project created
   */
  static notifyProjectCreated(projectName: string, projectId: string) {
    useNotificationStore.getState().addNotification({
      type: 'success',
      category: 'system',
      title: 'New project created',
      message: `Project "${projectName}" has been created`,
      projectId,
    });
  }

  /**
   * Create notification for processing error
   */
  static notifyError(title: string, message: string) {
    useNotificationStore.getState().addNotification({
      type: 'error',
      category: 'system',
      title,
      message,
    });
  }

  /**
   * Create notification for processing success
   */
  static notifySuccess(title: string, message: string) {
    useNotificationStore.getState().addNotification({
      type: 'success',
      category: 'system',
      title,
      message,
    });
  }
}

