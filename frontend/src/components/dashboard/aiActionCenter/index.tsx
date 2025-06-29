'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Upload,
  Brain,
  TrendingUp,
  PenTool,
  FileText,
  Eye,
  CheckCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';
import {
  generalApi,
  userWhispererApi,
  marketMavenApi,
  narrativeArchitectApi,
  DashboardStats,
  AgentActivity,
} from '@/lib/api/agents';

export default function AIActionCenter() {
  const { data: session } = useSession();
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [agentHealth, setAgentHealth] = useState({
    user_whisperer: false,
    market_maven: false,
    narrative_architect: false,
  });

  // Load dashboard data
  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);

      try {
        // Check agent health
        const healthResponse = await generalApi.healthCheckAll();
        if (healthResponse.success) {
          setAgentHealth(healthResponse.data);
        }

        // Load dashboard stats
        const statsResponse = await generalApi.getDashboardStats();
        if (statsResponse.success) {
          const data = statsResponse.data as any; // Temporary type assertion
          setStats({
            total_transcripts: data.total_transcripts || 0,
            completed_transcripts: data.completed_transcripts || 0,
            active_competitor_watches: data.active_competitor_watches || 0,
            recent_competitor_updates: data.recent_competitor_updates || 0,
            generated_content_pieces: data.generated_content_pieces || 0,
            agent_activities_today: data.agent_activities_today || 0,
          });
        }

        // Load recent activities (mock for now - would come from a combined activities endpoint)
        const [transcripts, competitorUpdates, content] = await Promise.all([
          userWhispererApi.getTranscripts(),
          marketMavenApi.getCompetitorUpdates('new', 5),
          narrativeArchitectApi.getAllContent(undefined, undefined, 5),
        ]);

        const mockActivities: AgentActivity[] = [];

        // Add transcript activities
        if (transcripts.success && transcripts.data?.transcripts) {
          transcripts.data.transcripts
            .slice(0, 3)
            .forEach((transcript: any) => {
              mockActivities.push({
                id: `transcript-${transcript.id}`,
                agent_type: 'user_whisperer',
                action_type: 'transcript_processed',
                title: `${transcript.title} Processed`,
                description: `Extracted insights from customer feedback`,
                status:
                  transcript.status === 'completed'
                    ? 'completed'
                    : transcript.status === 'processing'
                    ? 'processing'
                    : 'new',
                created_at: transcript.created_at,
              });
            });
        }

        // Add competitor update activities
        if (competitorUpdates.success && competitorUpdates.data) {
          competitorUpdates.data.slice(0, 2).forEach((update: any) => {
            mockActivities.push({
              id: `competitor-${update.id}`,
              agent_type: 'market_maven',
              action_type: 'competitor_analyzed',
              title: `${update.competitor_name} Update Detected`,
              description: update.title,
              status: 'new',
              created_at: update.detected_at,
            });
          });
        }

        // Add content generation activities
        if (content.success && content.data?.content) {
          content.data.content.slice(0, 2).forEach((item: any) => {
            mockActivities.push({
              id: `content-${item.content_id}`,
              agent_type: 'narrative_architect',
              action_type: 'content_generated',
              title: `${item.platform} Content Ready`,
              description: item.title || `${item.content_type} generated`,
              status: item.status === 'draft' ? 'completed' : 'new',
              created_at: item.created_at,
            });
          });
        }

        // Sort activities by date
        mockActivities.sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setActivities(mockActivities.slice(0, 5));
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'user_whisperer':
        return <Brain className="h-5 w-5" />;
      case 'market_maven':
        return <TrendingUp className="h-5 w-5" />;
      case 'narrative_architect':
        return <PenTool className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <Badge variant="default" className="bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Completed
          </Badge>
        );
      case 'processing':
        return (
          <Badge variant="default" className="bg-blue-100 text-blue-800">
            <Clock className="h-3 w-3 mr-1" />
            Processing
          </Badge>
        );
      case 'error':
        return (
          <Badge variant="destructive">
            <AlertCircle className="h-3 w-3 mr-1" />
            Error
          </Badge>
        );
      case 'new':
        return (
          <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
            <Eye className="h-3 w-3 mr-1" />
            Review Needed
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getAgentName = (agentType: string) => {
    switch (agentType) {
      case 'user_whisperer':
        return 'User Whisperer';
      case 'market_maven':
        return 'Market Maven';
      case 'narrative_architect':
        return 'Narrative Architect';
      default:
        return 'AI Agent';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Transcripts Processed
                </p>
                <p className="text-2xl font-bold">
                  {stats?.completed_transcripts}/{stats?.total_transcripts}
                </p>
              </div>
              <div className="flex flex-col items-center">
                <Brain className="h-8 w-8 text-blue-600" />
                <div
                  className={`w-2 h-2 rounded-full mt-1 ${
                    agentHealth.user_whisperer ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Competitor Watches
                </p>
                <p className="text-2xl font-bold">
                  {stats?.active_competitor_watches || 0}
                </p>
              </div>
              <div className="flex flex-col items-center">
                <TrendingUp className="h-8 w-8 text-green-600" />
                <div
                  className={`w-2 h-2 rounded-full mt-1 ${
                    agentHealth.market_maven ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Content Generated
                </p>
                <p className="text-2xl font-bold">
                  {stats?.generated_content_pieces || 0}
                </p>
              </div>
              <div className="flex flex-col items-center">
                <PenTool className="h-8 w-8 text-purple-600" />
                <div
                  className={`w-2 h-2 rounded-full mt-1 ${
                    agentHealth.narrative_architect
                      ? 'bg-green-500'
                      : 'bg-red-500'
                  }`}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Agent Status
                </p>
                <p className="text-2xl font-bold">
                  {Object.values(agentHealth).filter(Boolean).length}/3
                </p>
              </div>
              <div className="flex flex-col items-center">
                <CheckCircle
                  className={`h-8 w-8 ${
                    Object.values(agentHealth).every(Boolean)
                      ? 'text-green-600'
                      : 'text-yellow-600'
                  }`}
                />
                <p className="text-xs text-gray-500 mt-1">Online</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Action Center */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-6 w-6" />
            AI Action Center
          </CardTitle>
          <p className="text-sm text-gray-600">
            Review and approve AI-generated insights and content
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {activities.length === 0 ? (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-600 mb-2">
                No recent activity
              </h3>
              <p className="text-gray-500">
                Upload a transcript or add competitors to get started
              </p>
            </div>
          ) : (
            activities.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start space-x-4 p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex-shrink-0">
                  {getAgentIcon(activity.agent_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900">
                        {getAgentName(activity.agent_type)}
                      </p>
                      <Badge variant="outline" className="text-xs">
                        {activity.action_type}
                      </Badge>
                    </div>
                    {getStatusBadge(activity.status)}
                  </div>
                  <h4 className="text-sm font-semibold text-gray-800 mb-1">
                    {activity.title}
                  </h4>
                  <p className="text-sm text-gray-600 mb-3">
                    {activity.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-gray-500">
                      {new Date(activity.created_at).toLocaleString()}
                    </p>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 mr-1" />
                        Review
                      </Button>
                      {activity.status === 'new' && (
                        <Button size="sm">
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Approve
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <Upload className="h-12 w-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Upload Transcript</h3>
            <p className="text-sm text-gray-600 mb-4">
              Let User Whisperer analyze customer feedback
            </p>
            <Button className="w-full">
              <Upload className="h-4 w-4 mr-2" />
              Upload File
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <TrendingUp className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Add Competitor</h3>
            <p className="text-sm text-gray-600 mb-4">
              Monitor competitor updates with Market Maven
            </p>
            <Button className="w-full" variant="outline">
              <TrendingUp className="h-4 w-4 mr-2" />
              Add Competitor
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <PenTool className="h-12 w-12 text-purple-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Generate Content</h3>
            <p className="text-sm text-gray-600 mb-4">
              Create social media posts with Narrative Architect
            </p>
            <Button className="w-full" variant="outline">
              <PenTool className="h-4 w-4 mr-2" />
              Generate Content
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
