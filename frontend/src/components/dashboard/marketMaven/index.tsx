'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  TrendingUp,
  Eye,
  AlertTriangle,
  CheckCircle,
  Clock,
  ExternalLink,
  Plus,
  Target,
  BarChart3,
} from 'lucide-react';
import { marketMavenApi, type CompetitorUpdate } from '@/lib/api/agents';

interface AnalysisResult {
  executive_summary: string;
  key_updates: Array<{
    update_type: string;
    summary: string;
    impact_level: 'high' | 'medium' | 'low';
    implications: string;
    recommended_actions: string[];
    timeline: string;
  }>;
  market_trends: Array<{
    trend: string;
    implications: string;
  }>;
  strategic_recommendations: Array<{
    priority: 'high' | 'medium' | 'low';
    recommendation: string;
    rationale: string;
  }>;
  competitive_positioning: {
    strengths: string[];
    weaknesses: string[];
    differentiation_opportunities: string[];
  };
  threat_assessment: 'high' | 'medium' | 'low';
  monitoring_alerts: string[];
  confidence_level: 'high' | 'medium' | 'low';
}

export default function MarketMavenComponent() {
  const [competitorData, setCompetitorData] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(
    null
  );
  const [recentUpdates, setRecentUpdates] = useState<CompetitorUpdate[]>([]);
  const [loading, setLoading] = useState(true);

  // Load recent competitor updates
  const loadRecentUpdates = useCallback(async () => {
    setLoading(true);
    const response = await marketMavenApi.getCompetitorUpdates();
    if (response.success && response.data) {
      setRecentUpdates(response.data);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadRecentUpdates();
  }, [loadRecentUpdates]);

  // Handle competitor analysis
  const handleAnalyzeCompetitor = async () => {
    if (!competitorData.trim()) return;

    setIsAnalyzing(true);
    try {
      const response = await marketMavenApi.analyzeCompetitor(competitorData);

      if (response.success && response.data?.activity_id) {
        // Poll for results
        pollAnalysisResults(response.data.activity_id);
      } else {
        alert(`Analysis failed: ${response.error}`);
        setIsAnalyzing(false);
      }
    } catch (error) {
      alert(`Analysis error: ${error}`);
      setIsAnalyzing(false);
    }
  };

  // Poll analysis results
  const pollAnalysisResults = useCallback(async (activityId: string) => {
    const maxAttempts = 30; // 30 attempts = 5 minutes
    let attempts = 0;

    const poll = async () => {
      attempts++;
      const response = await marketMavenApi.getAnalysisStatus(activityId);

      if (response.success) {
        const status = response.data.status;

        if (status === 'success') {
          // Get the results
          const resultsResponse = await marketMavenApi.getAnalysisResults(
            activityId
          );
          if (resultsResponse.success && resultsResponse.data?.results) {
            setAnalysisResults(resultsResponse.data.results);
          }
          setIsAnalyzing(false);
          return; // Stop polling
        } else if (status === 'error') {
          alert('Analysis failed. Please try again.');
          setIsAnalyzing(false);
          return; // Stop polling
        }

        if (attempts < maxAttempts) {
          setTimeout(poll, 10000); // Poll every 10 seconds
        } else {
          setIsAnalyzing(false);
        }
      }
    };

    setTimeout(poll, 5000); // Start polling after 5 seconds
  }, []);

  const getThreatBadge = (level: string) => {
    switch (level) {
      case 'high':
        return (
          <Badge variant="destructive">
            <AlertTriangle className="h-3 w-3 mr-1" />
            High Threat
          </Badge>
        );
      case 'medium':
        return (
          <Badge variant="default" className="bg-yellow-100 text-yellow-800">
            <Eye className="h-3 w-3 mr-1" />
            Medium Threat
          </Badge>
        );
      case 'low':
        return (
          <Badge variant="outline" className="bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Low Threat
          </Badge>
        );
      default:
        return <Badge variant="outline">{level}</Badge>;
    }
  };

  const getImpactBadge = (level: string) => {
    switch (level) {
      case 'high':
        return <Badge variant="destructive">High Impact</Badge>;
      case 'medium':
        return (
          <Badge variant="default" className="bg-yellow-100 text-yellow-800">
            Medium Impact
          </Badge>
        );
      case 'low':
        return <Badge variant="outline">Low Impact</Badge>;
      default:
        return <Badge variant="outline">{level}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return <Badge variant="destructive">High Priority</Badge>;
      case 'medium':
        return (
          <Badge variant="default" className="bg-yellow-100 text-yellow-800">
            Medium Priority
          </Badge>
        );
      case 'low':
        return <Badge variant="outline">Low Priority</Badge>;
      default:
        return <Badge variant="outline">{priority}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="h-6 w-6 text-green-600" />
        <h2 className="text-2xl font-bold">Market Maven</h2>
        <Badge variant="outline">Competitive Intelligence</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analysis Input */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Analyze Competitor
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="competitor-data">Competitor Information</Label>
              <Textarea
                id="competitor-data"
                value={competitorData}
                onChange={(e) => setCompetitorData(e.target.value)}
                placeholder="Enter competitor data: website content, press releases, product announcements, pricing changes, etc."
                rows={8}
              />
              <p className="text-sm text-gray-500 mt-1">
                Paste competitor information you want to analyze
              </p>
            </div>

            <Button
              onClick={handleAnalyzeCompetitor}
              disabled={!competitorData.trim() || isAnalyzing}
              className="w-full">
              {isAnalyzing ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analyze Competition
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Recent Updates */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Recent Updates
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentUpdates.length === 0 ? (
              <div className="text-center py-8">
                <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No recent competitor updates</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentUpdates.slice(0, 5).map((update) => (
                  <div
                    key={update.id}
                    className="p-3 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">
                          {update.competitor_name}
                        </p>
                        <p className="text-sm text-gray-600">{update.title}</p>
                      </div>
                      <Badge variant="outline" className="ml-2 text-xs">
                        {update.update_type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500">
                      {new Date(update.detected_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Analysis Results */}
      {analysisResults && (
        <div className="space-y-6">
          {/* Executive Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Competitive Intelligence Report</span>
                {getThreatBadge(analysisResults.threat_assessment)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <h4 className="font-semibold mb-3">Executive Summary</h4>
                <p className="text-gray-700 mb-4">
                  {analysisResults.executive_summary}
                </p>

                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>
                    Confidence Level: {analysisResults.confidence_level}
                  </span>
                  <span>•</span>
                  <span>
                    Threat Assessment: {analysisResults.threat_assessment}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Key Updates */}
          {analysisResults.key_updates?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Key Updates</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysisResults.key_updates.map((update, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-semibold">
                        {update.update_type.replace('_', ' ').toUpperCase()}
                      </h5>
                      {getImpactBadge(update.impact_level)}
                    </div>
                    <p className="text-gray-700 mb-3">{update.summary}</p>
                    <div className="space-y-2">
                      <div>
                        <h6 className="font-medium text-sm">Implications:</h6>
                        <p className="text-sm text-gray-600">
                          {update.implications}
                        </p>
                      </div>
                      <div>
                        <h6 className="font-medium text-sm">
                          Recommended Actions:
                        </h6>
                        <ul className="text-sm text-gray-600 list-disc list-inside">
                          {update.recommended_actions.map(
                            (action, actionIndex) => (
                              <li key={actionIndex}>{action}</li>
                            )
                          )}
                        </ul>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        Timeline: {update.timeline}
                      </Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Strategic Recommendations */}
          {analysisResults.strategic_recommendations?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Strategic Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysisResults.strategic_recommendations.map((rec, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-semibold">{rec.recommendation}</h5>
                      {getPriorityBadge(rec.priority)}
                    </div>
                    <p className="text-sm text-gray-600">{rec.rationale}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Market Trends */}
          {analysisResults.market_trends?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Market Trends Identified</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {analysisResults.market_trends.map((trend, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4">
                    <h5 className="font-medium">{trend.trend}</h5>
                    <p className="text-sm text-gray-600">
                      {trend.implications}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Competitive Positioning */}
          {analysisResults.competitive_positioning && (
            <Card>
              <CardHeader>
                <CardTitle>Competitive Positioning Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h5 className="font-semibold text-green-700 mb-3">
                      Strengths
                    </h5>
                    <ul className="space-y-1">
                      {analysisResults.competitive_positioning.strengths.map(
                        (strength, index) => (
                          <li
                            key={index}
                            className="text-sm p-2 bg-green-50 rounded">
                            {strength}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-semibold text-red-700 mb-3">
                      Weaknesses
                    </h5>
                    <ul className="space-y-1">
                      {analysisResults.competitive_positioning.weaknesses.map(
                        (weakness, index) => (
                          <li
                            key={index}
                            className="text-sm p-2 bg-red-50 rounded">
                            {weakness}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-semibold text-blue-700 mb-3">
                      Opportunities
                    </h5>
                    <ul className="space-y-1">
                      {analysisResults.competitive_positioning.differentiation_opportunities.map(
                        (opp, index) => (
                          <li
                            key={index}
                            className="text-sm p-2 bg-blue-50 rounded">
                            {opp}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Monitoring Alerts */}
          {analysisResults.monitoring_alerts?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Monitoring Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {analysisResults.monitoring_alerts.map((alert, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 p-3 bg-yellow-50 rounded-lg">
                      <Eye className="h-4 w-4 text-yellow-600" />
                      <span className="text-sm">{alert}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
