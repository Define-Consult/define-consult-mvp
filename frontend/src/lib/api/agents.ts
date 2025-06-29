/**
 * API Client for Define Consult AI Agents
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const USE_TEST_MODE = process.env.NODE_ENV === 'development'; // Use test endpoints in development

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// Base API client function
async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
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

// User Whisperer Agent API
export const userWhispererApi = {
  // Upload transcript
  async uploadTranscript(
    file: File,
    title: string = '',
    description: string = ''
  ) {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);

    const endpoint = USE_TEST_MODE
      ? '/agents/user-whisperer/test/upload-transcript'
      : '/agents/user-whisperer/upload';

    return apiRequest(endpoint, {
      method: 'POST',
      headers: {}, // Don't set Content-Type for FormData
      body: formData,
    });
  },

  // Get transcripts
  async getTranscripts() {
    const endpoint = USE_TEST_MODE
      ? '/agents/user-whisperer/test/transcripts'
      : '/agents/user-whisperer/transcripts';
    return apiRequest(endpoint);
  },

  // Get specific transcript
  async getTranscript(transcriptId: string) {
    const endpoint = USE_TEST_MODE
      ? `/agents/user-whisperer/test/transcripts/${transcriptId}`
      : `/agents/user-whisperer/transcripts/${transcriptId}`;
    return apiRequest(endpoint);
  },

  // Get transcript insights
  async getTranscriptInsights(transcriptId: string) {
    const endpoint = USE_TEST_MODE
      ? `/agents/user-whisperer/test/transcripts/${transcriptId}/insights`
      : `/agents/user-whisperer/transcripts/${transcriptId}/insights`;
    return apiRequest(endpoint);
  },

  // Check health
  async health() {
    return apiRequest('/agents/user-whisperer/health');
  },
};

// Market Maven Agent API
export const marketMavenApi = {
  // Analyze competitor data
  analyzeCompetitor: async (competitorData: string) => {
    const endpoint = USE_TEST_MODE
      ? '/agents/market-maven/test/analyze'
      : '/agents/market-maven/analyze';
    return apiRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify({ competitor_data: competitorData }),
    });
  },

  // Get analysis status
  getAnalysisStatus: async (activityId: string) => {
    const endpoint = USE_TEST_MODE
      ? `/agents/market-maven/test/analysis/${activityId}/status`
      : `/agents/market-maven/analysis/${activityId}/status`;
    return apiRequest(endpoint);
  },

  // Get analysis results
  getAnalysisResults: async (activityId: string) => {
    const endpoint = USE_TEST_MODE
      ? `/agents/market-maven/test/analysis/${activityId}/results`
      : `/agents/market-maven/analysis/${activityId}/results`;
    return apiRequest(endpoint);
  },

  // Create competitor watch
  createCompetitorWatch: async (
    competitorName: string,
    websiteUrl: string,
    checkFrequency: string = 'daily'
  ) => {
    return apiRequest('/agents/market-maven/competitor-watches', {
      method: 'POST',
      body: JSON.stringify({
        competitor_name: competitorName,
        website_url: websiteUrl,
        check_frequency: checkFrequency,
      }),
    });
  },

  // Get competitor watches
  getCompetitorWatches: async () => {
    return apiRequest('/agents/market-maven/competitor-watches');
  },

  // Get competitor updates
  getCompetitorUpdates: async (status?: string, limit: number = 20) => {
    if (USE_TEST_MODE) {
      return apiRequest('/test/agents/market-maven/updates');
    }

    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit.toString());

    return apiRequest(`/agents/market-maven/updates?${params.toString()}`);
  },

  // Health check
  health: async () => {
    return apiRequest('/agents/market-maven/health');
  },
};

// Narrative Architect Agent API
export const narrativeArchitectApi = {
  // Generate content
  generateContent: async (
    sourceMaterial: string,
    platform: string = 'linkedin',
    contentType: string = 'social_post'
  ) => {
    return apiRequest('/agents/narrative-architect/test/generate', {
      method: 'POST',
      body: JSON.stringify({
        source_material: sourceMaterial,
        platform,
        content_type: contentType,
      }),
    });
  },

  // Get content status
  getContentStatus: async (contentId: string) => {
    return apiRequest(
      `/agents/narrative-architect/test/content/${contentId}/status`
    );
  },

  // Get content
  getContent: async (contentId: string) => {
    return apiRequest(`/agents/narrative-architect/test/content/${contentId}`);
  },

  // Get all content
  getAllContent: async (
    contentType?: string,
    platform?: string,
    limit: number = 20
  ) => {
    if (USE_TEST_MODE) {
      return apiRequest('/test/agents/narrative-architect/content');
    }

    const params = new URLSearchParams();
    if (contentType) params.append('content_type', contentType);
    if (platform) params.append('platform', platform);
    params.append('limit', limit.toString());

    return apiRequest(
      `/agents/narrative-architect/content?${params.toString()}`
    );
  },

  // Health check
  health: async () => {
    return apiRequest('/agents/narrative-architect/health');
  },
};

// General API functions
export const generalApi = {
  // Get dashboard stats
  getDashboardStats: async () => {
    // In development/test mode, use test endpoint
    if (USE_TEST_MODE) {
      try {
        // Use the test dashboard stats endpoint that doesn't require auth
        const testStats = await apiRequest('/test/dashboard/stats');
        if (testStats.success) {
          return testStats;
        }
      } catch (error) {
        console.warn(
          'Test stats endpoint not available, calculating from agents'
        );
      }
    }

    // Fallback to calculating stats from individual agent endpoints
    const [transcripts, competitorUpdates, content] = await Promise.all([
      userWhispererApi.getTranscripts(),
      marketMavenApi.getCompetitorUpdates(),
      narrativeArchitectApi.getAllContent(),
    ]);

    // Calculate stats from responses
    const stats = {
      total_transcripts: transcripts.success
        ? transcripts.data?.transcripts?.length || 0
        : 0,
      completed_transcripts: transcripts.success
        ? transcripts.data?.transcripts?.filter(
            (t: any) => t.status === 'completed'
          )?.length || 0
        : 0,
      active_competitor_watches: competitorUpdates.success
        ? competitorUpdates.data?.length || 0
        : 0,
      recent_competitor_updates: competitorUpdates.success
        ? competitorUpdates.data?.length || 0
        : 0,
      generated_content_pieces: content.success
        ? content.data?.content?.length || 0
        : 0,
      agent_activities_today: 0, // Would need a separate endpoint to calculate this
    };

    return {
      success: true,
      data: stats,
    };
  },

  // Health check all agents
  healthCheckAll: async () => {
    // In development/test mode, use test endpoint
    if (USE_TEST_MODE) {
      try {
        const testHealth = await apiRequest('/test/agents/health');
        if (testHealth.success) {
          return testHealth;
        }
      } catch (error) {
        console.warn(
          'Test health endpoint not available, checking agents individually'
        );
      }
    }

    // Try to use the combined health endpoint
    try {
      const combinedHealth = await apiRequest('/agents/health');
      if (combinedHealth.success) {
        return combinedHealth;
      }
    } catch (error) {
      console.warn(
        'Combined health endpoint not available, checking agents individually'
      );
    }

    // Fallback to individual agent health checks
    const [userWhisperer, marketMaven, narrativeArchitect] = await Promise.all([
      userWhispererApi.health(),
      marketMavenApi.health(),
      narrativeArchitectApi.health(),
    ]);

    return {
      success: true,
      data: {
        user_whisperer: userWhisperer.success,
        market_maven: marketMaven.success,
        narrative_architect: narrativeArchitect.success,
      },
    };
  },
};

// Types
export interface Transcript {
  id: string;
  title: string;
  status: 'uploaded' | 'processing' | 'completed' | 'error';
  file_metadata: {
    original_filename: string;
    file_size: number;
    upload_timestamp: string;
  };
  analysis?: any;
  insights?: string[];
  sentiment_score?: number;
  key_themes?: string[];
  pain_points?: string[];
  feature_requests?: string[];
  created_at: string;
  updated_at?: string;
}

export interface CompetitorWatch {
  id: string;
  competitor_name: string;
  website_url: string;
  is_active: boolean;
  check_frequency: string;
  last_checked_at?: string;
  created_at: string;
}

export interface CompetitorUpdate {
  id: string;
  competitor_name: string;
  update_type: string;
  title: string;
  ai_summary?: string;
  ai_impact_analysis?: string;
  status: string;
  detected_at: string;
}

export interface GeneratedContent {
  content_id: string;
  platform: string;
  content_type: string;
  title?: string;
  content: string;
  status: 'draft' | 'approved' | 'published' | 'rejected';
  source_data?: any;
  created_at: string;
  updated_at?: string;
}

export interface AgentActivity {
  id: string;
  agent_type: 'user_whisperer' | 'market_maven' | 'narrative_architect';
  action_type: string;
  title: string;
  description: string;
  status: 'new' | 'processing' | 'completed' | 'error';
  created_at: string;
}

export interface DashboardStats {
  total_transcripts: number;
  completed_transcripts: number;
  active_competitor_watches: number;
  recent_competitor_updates: number;
  generated_content_pieces: number;
  agent_activities_today: number;
}
