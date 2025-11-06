/**
 * Notification Store (Zustand)
 * State management for notifications and alerts
 */

import { create } from 'zustand';
import { apiClient } from '../services/api';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationCategory = 'new_project_email' | 'low_confidence' | 'multi_project' | 'system';

export interface Notification {
  id: string;
  type: NotificationType;
  category: NotificationCategory;
  title: string;
  message: string;
  projectId?: string;
  emailId?: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  actionLabel?: string;
}

interface NotificationStore {
  notifications: Notification[];
  unreadCount: number;
  isSoundEnabled: boolean;
  
  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  loadNotifications: () => Promise<void>;
  toggleSound: () => void;
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isSoundEnabled: true,

  addNotification: (notification) => {
    const newNotification: Notification = {
      ...notification,
      id: `notification-${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
      read: false,
    };

    set((state) => ({
      notifications: [newNotification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }));

    // Play sound if enabled
    if (get().isSoundEnabled) {
      // Optional: Play a subtle notification sound
      // new Audio('/notification.mp3').play().catch(() => {});
    }

    // Auto-dismiss after 5 seconds for non-critical notifications
    if (notification.type !== 'error') {
      setTimeout(() => {
        get().removeNotification(newNotification.id);
      }, 5000);
    }
  },

  markAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    }));
  },

  markAllAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    }));
  },

  removeNotification: (id) => {
    set((state) => {
      const notification = state.notifications.find((n) => n.id === id);
      return {
        notifications: state.notifications.filter((n) => n.id !== id),
        unreadCount: notification && !notification.read
          ? Math.max(0, state.unreadCount - 1)
          : state.unreadCount,
      };
    });
  },

  clearAll: () => {
    set({
      notifications: [],
      unreadCount: 0,
    });
  },

  loadNotifications: async () => {
    try {
      // TODO: Load from backend API when endpoint is available
      // const data = await apiClient.getNotifications();
      // set({ notifications: data });
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  },

  toggleSound: () => {
    set((state) => ({
      isSoundEnabled: !state.isSoundEnabled,
    }));
  },
}));

