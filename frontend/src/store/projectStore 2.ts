/**
 * Project Store (Zustand)
 * State management for projects and UI state
 */

import { create } from 'zustand';
import { apiClient } from '../services/api';

interface Project {
  id: number;
  project_id: string;
  project_name: string;
  address?: string;
  client_name?: string;
  project_type?: string;
  email_count: number;
  last_email_at?: string;
  status: string;
  needs_review: boolean;
}

interface ProjectStore {
  projects: Project[];
  selectedProjectId: string | null;
  searchQuery: string;
  filterStatus: string | null;
  isLoading: boolean;
  error: string | null;
  isCollapsed: boolean;
  
  // Actions
  loadProjects: (status?: string) => Promise<void>;
  selectProject: (projectId: string | null) => void;
  setSearchQuery: (query: string) => void;
  setFilterStatus: (status: string | null) => void;
  toggleCollapse: () => void;
  refreshProjects: () => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  selectedProjectId: null,
  searchQuery: '',
  filterStatus: null,
  isLoading: false,
  error: null,
  isCollapsed: false,

  loadProjects: async (status?: string) => {
    set({ isLoading: true, error: null });
    try {
      const projects = await apiClient.getProjects(status);
      set({ projects, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to load projects',
        isLoading: false 
      });
    }
  },

  selectProject: (projectId: string | null) => {
    set({ selectedProjectId: projectId });
  },

  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
  },

  setFilterStatus: (status: string | null) => {
    set({ filterStatus: status });
  },

  toggleCollapse: () => {
    set((state) => ({ isCollapsed: !state.isCollapsed }));
  },

  refreshProjects: async () => {
    const { filterStatus } = get();
    await get().loadProjects(filterStatus || undefined);
  },
}));

