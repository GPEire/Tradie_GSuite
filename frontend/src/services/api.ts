/**
 * API Client for Backend Communication
 * Handles all API calls to the backend service
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from storage
    this.loadToken();

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          await this.refreshToken();
        }
        return Promise.reject(error);
      }
    );
  }

  private async loadToken(): Promise<void> {
    try {
      const result = await chrome.storage.local.get(['auth_token']);
      this.token = result.auth_token || null;
    } catch (error) {
      console.error('Error loading token:', error);
    }
  }

  private async refreshToken(): Promise<void> {
    // TODO: Implement token refresh
    this.token = null;
  }

  async setToken(token: string): Promise<void> {
    this.token = token;
    await chrome.storage.local.set({ auth_token: token });
  }

  // Projects API
  async getProjects(status?: string) {
    const params = status ? { status } : {};
    const response = await this.client.get('/api/v1/projects', { params });
    return response.data;
  }

  async getProject(projectId: string) {
    const response = await this.client.get(`/api/v1/projects/${projectId}`);
    return response.data;
  }

  async detectProjectForEmail(emailData: any, autoCreate: boolean = true) {
    const response = await this.client.post('/api/v1/projects/detect', null, {
      params: { auto_create: autoCreate, confidence_threshold: 0.7 },
      data: emailData,
    });
    return response.data;
  }

  // Scanning API
  async startScanning() {
    const response = await this.client.post('/api/v1/scanning/start');
    return response.data;
  }

  async scanOnDemand(limit: number = 100) {
    const response = await this.client.post('/api/v1/scanning/scan', null, {
      params: { limit },
    });
    return response.data;
  }

  // Gmail API
  async getGmailProfile() {
    const response = await this.client.get('/api/v1/gmail/profile');
    return response.data;
  }

  async listEmails(query: string = '', maxResults: number = 50) {
    const response = await this.client.get('/api/v1/gmail/messages', {
      params: { query, max_results: maxResults },
    });
    return response.data;
  }

  // Processing API
  async processPendingQueue(limit: number = 50) {
    const response = await this.client.post('/api/v1/processing/queue/process', null, {
      params: { limit },
    });
    return response.data;
  }

  // Project Emails API
  async getProjectEmails(projectId: string) {
    const response = await this.client.get(`/api/v1/projects/${projectId}/emails`);
    return response.data;
  }

  // Attachments API
  async getProjectAttachments(projectId: string) {
    const response = await this.client.get(`/api/v1/scanning/attachments/project/${projectId}`);
    return response.data;
  }

  async getEmailAttachments(emailId: string) {
    const response = await this.client.get(`/api/v1/scanning/attachments/${emailId}`);
    return response.data;
  }

  // Project Management API
  async addEmailToProject(projectId: string, emailId: string, threadId?: string, method: string = 'manual') {
    const response = await this.client.post(`/api/v1/projects/${projectId}/emails`, null, {
      params: { email_id: emailId, thread_id: threadId, method },
    });
    return response.data;
  }

  async removeEmailFromProject(projectId: string, emailId: string) {
    // TODO: Implement backend endpoint
    const response = await this.client.delete(`/api/v1/projects/${projectId}/emails/${emailId}`);
    return response.data;
  }

  async updateProject(projectId: string, updates: { project_name?: string; status?: string; address?: string }) {
    // TODO: Implement backend endpoint
    const response = await this.client.patch(`/api/v1/projects/${projectId}`, updates);
    return response.data;
  }

  async deleteProject(projectId: string) {
    // TODO: Implement backend endpoint
    const response = await this.client.delete(`/api/v1/projects/${projectId}`);
    return response.data;
  }

  async mergeProjects(sourceProjectId: string, targetProjectId: string) {
    // TODO: Implement backend endpoint
    const response = await this.client.post(`/api/v1/projects/${sourceProjectId}/merge`, null, {
      params: { target_project_id: targetProjectId },
    });
    return response.data;
  }

  async splitProject(projectId: string, emailIds: string[], newProjectName: string) {
    // TODO: Implement backend endpoint
    const response = await this.client.post(`/api/v1/projects/${projectId}/split`, {
      email_ids: emailIds,
      new_project_name: newProjectName,
    });
    return response.data;
  }

  // Learning/Correction API
  async recordCorrection(correction: {
    correction_type: string;
    original_result: any;
    corrected_result: any;
    email_id?: string;
    project_id?: string;
    correction_reason?: string;
  }) {
    const response = await this.client.post('/api/v1/processing/learning/correction', correction);
    return response.data;
  }

  async submitFeedback(feedback: {
    feedback_type: string;
    rating?: number;
    comment?: string;
    context?: any;
  }) {
    const response = await this.client.post('/api/v1/processing/learning/feedback', feedback);
    return response.data;
  }

  // Notifications API
  async getNotifications(limit: number = 50) {
    // TODO: Implement backend endpoint
    const response = await this.client.get('/api/v1/notifications', {
      params: { limit },
    });
    return response.data;
  }

  async markNotificationAsRead(notificationId: string) {
    // TODO: Implement backend endpoint
    const response = await this.client.patch(`/api/v1/notifications/${notificationId}/read`);
    return response.data;
  }

  // Configuration API
  async getScanConfiguration() {
    const response = await this.client.get('/api/v1/scanning/config');
    return response.data;
  }

  async updateScanConfiguration(config: any) {
    const response = await this.client.put('/api/v1/scanning/config', config);
    return response.data;
  }

  async getGmailLabels() {
    const response = await this.client.get('/api/v1/gmail/labels');
    return response.data;
  }

  async getProjectNamingConfig() {
    // TODO: Implement backend endpoint
    try {
      const response = await this.client.get('/api/v1/config/project-naming');
      return response.data;
    } catch {
      return { rules: [], label_format: 'project_{name}', auto_create_labels: true };
    }
  }

  async updateProjectNamingConfig(config: any) {
    // TODO: Implement backend endpoint
    const response = await this.client.put('/api/v1/config/project-naming', config);
    return response.data;
  }

  async getIntegrationSettings() {
    // TODO: Implement backend endpoint
    try {
      const response = await this.client.get('/api/v1/config/integrations');
      return response.data;
    } catch {
      return {
        google_drive_enabled: false,
        google_contacts_enabled: false,
        calendar_enabled: false,
        drive_auto_upload: false,
        contacts_auto_sync: false,
      };
    }
  }

  async updateIntegrationSettings(settings: any) {
    // TODO: Implement backend endpoint
    const response = await this.client.put('/api/v1/config/integrations', settings);
    return response.data;
  }
}

export const apiClient = new ApiClient();

