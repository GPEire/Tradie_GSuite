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
}

export const apiClient = new ApiClient();

