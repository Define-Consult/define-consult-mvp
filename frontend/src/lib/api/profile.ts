/**
 * API Client for User Profiles and Billing
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const USE_TEST_MODE = process.env.NODE_ENV === 'development';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// Base API client function with auth support
async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    // Get auth token from NextAuth session if available
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // In a real implementation, you'd get the Firebase ID token here
    // For now, we'll rely on the test endpoints in development

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers,
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.detail || data.message || 'An error occurred',
      };
    }

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

// User Profile API
export const userProfileApi = {
  // Get current user profile
  async getProfile() {
    const endpoint = USE_TEST_MODE ? '/users/test/me' : '/users/me';
    return apiRequest(endpoint);
  },

  // Update user profile
  async updateProfile(profileData: {
    name?: string;
    company_name?: string;
    role_at_company?: string;
    industry?: string;
    linkedin_profile_url?: string;
    notification_preferences?: {
      email_digest?: boolean;
      slack_alerts?: boolean;
      in_app_notifications?: boolean;
      marketing_emails?: boolean;
    };
    brand_tone_preferences?: {
      formal?: number;
      friendly?: number;
      professional?: number;
      creative?: number;
    };
  }) {
    const endpoint = USE_TEST_MODE ? '/users/test/me' : '/users/me';
    return apiRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },

  // Delete user account
  async deleteAccount() {
    const endpoint = '/users/me';
    return apiRequest(endpoint, {
      method: 'DELETE',
    });
  },
};

// Billing API
export const billingApi = {
  // Get available plans
  async getPlans() {
    const endpoint = USE_TEST_MODE ? '/billing/test/plans' : '/billing/plans';
    return apiRequest(endpoint);
  },

  // Get current usage
  async getUsage() {
    const endpoint = USE_TEST_MODE ? '/billing/test/usage' : '/billing/usage';
    return apiRequest(endpoint);
  },

  // Create checkout session for plan upgrade
  async createCheckoutSession(
    planId: string,
    successUrl: string,
    cancelUrl: string
  ) {
    return apiRequest('/billing/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({
        plan_id: planId,
        success_url: successUrl,
        cancel_url: cancelUrl,
      }),
    });
  },

  // Get subscription management URL
  async getManageSubscriptionUrl() {
    return apiRequest('/billing/manage-subscription');
  },
};

// Team Management API (placeholder for future implementation)
export const teamApi = {
  // Get current team
  async getCurrentTeam() {
    // Placeholder - would implement when team functionality is added
    return {
      success: true,
      data: null,
    };
  },

  // Create team
  async createTeam(teamName: string) {
    return apiRequest('/teams', {
      method: 'POST',
      body: JSON.stringify({ name: teamName }),
    });
  },

  // Invite team member
  async inviteTeamMember(email: string, role: 'admin' | 'member' = 'member') {
    return apiRequest('/teams/invite', {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    });
  },
};

// Notifications API (placeholder for future implementation)
export const notificationsApi = {
  // Get notifications
  async getNotifications() {
    // Placeholder - would implement when notification system is added
    return {
      success: true,
      data: [],
    };
  },

  // Mark notification as read
  async markAsRead(notificationId: string) {
    return apiRequest(`/notifications/${notificationId}/read`, {
      method: 'POST',
    });
  },

  // Update notification preferences
  async updatePreferences(preferences: any) {
    return apiRequest('/notifications/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  },
};

// Types
export interface UserProfile {
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
  usage_stats?: {
    total_agent_actions_this_month?: number;
    last_login?: string;
  };
  notification_preferences?: {
    email_digest?: boolean;
    slack_alerts?: boolean;
    in_app_notifications?: boolean;
    marketing_emails?: boolean;
  };
  brand_tone_preferences?: {
    formal?: number;
    friendly?: number;
    professional?: number;
    creative?: number;
  };
  created_at: string;
  updated_at: string;
}

export interface BillingPlan {
  id: string;
  name: string;
  price_usd_per_month: number;
  monthly_agent_action_limit: number;
  stripe_price_id: string;
  is_metered_billing: boolean;
  per_action_cost_usd?: number;
  available_integrations: string[];
  priority_support: boolean;
  is_team_plan: boolean;
}

export interface BillingUsage {
  current_plan: string;
  agent_actions_used: number;
  agent_actions_limit: number;
  billing_period_start: string;
  billing_period_end: string;
  estimated_cost: number;
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
  email: string;
  name?: string;
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
