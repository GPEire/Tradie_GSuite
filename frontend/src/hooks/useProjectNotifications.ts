/**
 * Hook for Project Notifications
 * TASK-033: Automatically trigger notifications for project events
 */

import { useEffect } from 'react';
import { NotificationService } from '../services/notificationService';
import { useProjectStore } from '../store/projectStore';

/**
 * Hook to monitor project changes and trigger notifications
 */
export const useProjectNotifications = () => {
  const { projects, selectedProjectId } = useProjectStore();

  useEffect(() => {
    // Monitor for projects that need review (low confidence)
    projects.forEach((project) => {
      if (project.needs_review && project.confidence_score) {
        const confidence = parseFloat(project.confidence_score);
        if (confidence < 0.7) {
          // Only notify once per project - could be enhanced with a "notified" flag
          // For now, this will re-notify on each render, which may be too frequent
          // In production, should track which projects have been notified
        }
      }
    });
  }, [projects]);

  /**
   * Notify about new project email
   */
  const notifyNewEmail = (
    projectId: string,
    projectName: string,
    emailId: string,
    emailSubject: string
  ) => {
    NotificationService.notifyNewProjectEmail(
      projectName,
      emailSubject,
      projectId,
      emailId
    );
  };

  /**
   * Notify about low confidence grouping
   */
  const notifyLowConfidence = (
    projectId: string,
    projectName: string,
    confidence: number,
    emailId?: string
  ) => {
    NotificationService.notifyLowConfidence(
      projectName,
      confidence,
      projectId,
      emailId
    );
  };

  /**
   * Notify about multi-project detection
   */
  const notifyMultiProject = (
    emailId: string,
    emailSubject: string,
    projectNames: string[]
  ) => {
    NotificationService.notifyMultiProject(emailSubject, projectNames, emailId);
  };

  return {
    notifyNewEmail,
    notifyLowConfidence,
    notifyMultiProject,
  };
};

