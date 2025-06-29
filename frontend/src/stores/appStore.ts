import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  company_name?: string;
  role_at_company?: string;
  industry?: string;
  linkedin_profile_url?: string;
  current_plan_id?: string;
  billing_customer_id?: string;
  usage_stats?: any;
  notification_preferences?: any;
  brand_tone_preferences?: any;
  created_at?: string;
  updated_at?: string;
}

export interface Team {
  id: string;
  name: string;
  created_by: string;
  members: TeamMember[];
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  user_id: string;
  role: 'admin' | 'member';
  joined_at: string;
}

export interface AppNotification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

interface AppState {
  // User & Auth
  user: User | null;
  isAuthenticated: boolean;

  // Team
  currentTeam: Team | null;

  // UI State
  sidebarOpen: boolean;
  notifications: AppNotification[];

  // Loading States
  isLoading: boolean;

  // Actions
  setUser: (user: User | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setCurrentTeam: (team: Team | null) => void;
  setSidebarOpen: (open: boolean) => void;
  addNotification: (
    notification: Omit<AppNotification, 'id' | 'timestamp'>
  ) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        isAuthenticated: false,
        currentTeam: null,
        sidebarOpen: false,
        notifications: [],
        isLoading: false,

        // Actions
        setUser: (user) => set({ user }, false, 'setUser'),

        setAuthenticated: (isAuthenticated) =>
          set({ isAuthenticated }, false, 'setAuthenticated'),

        setCurrentTeam: (team) =>
          set({ currentTeam: team }, false, 'setCurrentTeam'),

        setSidebarOpen: (open) =>
          set({ sidebarOpen: open }, false, 'setSidebarOpen'),

        addNotification: (notification) => {
          const newNotification: AppNotification = {
            ...notification,
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            read: false,
          };
          set(
            (state) => ({
              notifications: [newNotification, ...state.notifications].slice(
                0,
                50
              ), // Keep last 50
            }),
            false,
            'addNotification'
          );
        },

        markNotificationRead: (id) =>
          set(
            (state) => ({
              notifications: state.notifications.map((n) =>
                n.id === id ? { ...n, read: true } : n
              ),
            }),
            false,
            'markNotificationRead'
          ),

        clearNotifications: () =>
          set({ notifications: [] }, false, 'clearNotifications'),

        setLoading: (loading) =>
          set({ isLoading: loading }, false, 'setLoading'),
      }),
      {
        name: 'define-consult-app-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          currentTeam: state.currentTeam,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    ),
    {
      name: 'define-consult-app-store',
    }
  )
);
