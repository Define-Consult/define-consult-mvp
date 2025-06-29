'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  PenTool,
  Copy,
  Share,
  Clock,
  CheckCircle,
  Edit,
  Download,
  Eye,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';
import { narrativeArchitectApi, type GeneratedContent } from '@/lib/api/agents';

export default function NarrativeArchitectComponent() {
  const [sourceMaterial, setSourceMaterial] = useState('');
  const [platform, setPlatform] = useState('linkedin');
  const [contentType, setContentType] = useState('social_post');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContents, setGeneratedContents] = useState<
    GeneratedContent[]
  >([]);
  const [selectedContent, setSelectedContent] =
    useState<GeneratedContent | null>(null);
  const [loading, setLoading] = useState(true);

  // Load generated content
  const loadGeneratedContent = useCallback(async () => {
    setLoading(true);
    const response = await narrativeArchitectApi.getAllContent();
    if (response.success && response.data?.content) {
      setGeneratedContents(response.data.content);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadGeneratedContent();
  }, [loadGeneratedContent]);

  // Handle content generation
  const handleGenerateContent = async () => {
    if (!sourceMaterial.trim()) return;

    setIsGenerating(true);
    try {
      const response = await narrativeArchitectApi.generateContent(
        sourceMaterial,
        platform,
        contentType
      );

      if (response.success && response.data?.content_id) {
        // Poll for results
        pollContentResults(response.data.content_id);
      } else {
        alert(`Generation failed: ${response.error}`);
        setIsGenerating(false);
      }
    } catch (error) {
      alert(`Generation error: ${error}`);
      setIsGenerating(false);
    }
  };

  // Poll content results
  const pollContentResults = useCallback(async (contentId: string) => {
    const maxAttempts = 30; // 30 attempts = 5 minutes
    let attempts = 0;

    const poll = async () => {
      attempts++;
      const response = await narrativeArchitectApi.getContentStatus(contentId);

      if (response.success) {
        const status = response.data.status;

        if (status === 'draft') {
          // Get the content details
          const contentResponse = await narrativeArchitectApi.getContent(
            contentId
          );
          if (contentResponse.success) {
            setSelectedContent(contentResponse.data);
            setGeneratedContents((prev) => [contentResponse.data, ...prev]);
          }
          setIsGenerating(false);
          return; // Stop polling
        } else if (status === 'error') {
          alert('Content generation failed. Please try again.');
          setIsGenerating(false);
          return; // Stop polling
        }

        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setIsGenerating(false);
        }
      }
    };

    setTimeout(poll, 2000); // Start polling after 2 seconds
  }, []);

  // Copy content to clipboard
  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      alert('Content copied to clipboard!');
    } catch (error) {
      alert('Failed to copy content');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return (
          <Badge variant="outline" className="bg-blue-100 text-blue-800">
            <Edit className="h-3 w-3 mr-1" />
            Draft
          </Badge>
        );
      case 'approved':
        return (
          <Badge variant="default" className="bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Approved
          </Badge>
        );
      case 'published':
        return (
          <Badge variant="default" className="bg-purple-100 text-purple-800">
            <Share className="h-3 w-3 mr-1" />
            Published
          </Badge>
        );
      case 'rejected':
        return (
          <Badge variant="destructive">
            <ThumbsDown className="h-3 w-3 mr-1" />
            Rejected
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'linkedin':
        return '💼';
      case 'twitter':
        return '🐦';
      case 'facebook':
        return '📘';
      case 'medium':
        return '📝';
      default:
        return '📱';
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
        <PenTool className="h-6 w-6 text-purple-600" />
        <h2 className="text-2xl font-bold">Narrative Architect</h2>
        <Badge variant="outline">Content Generation</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Content Generation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PenTool className="h-5 w-5" />
              Generate Content
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="source-material">Source Material</Label>
              <Textarea
                id="source-material"
                value={sourceMaterial}
                onChange={(e) => setSourceMaterial(e.target.value)}
                placeholder="Enter feature description, product update, announcement, or any content you want to turn into social media posts..."
                rows={6}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="platform">Platform</Label>
                <Select value={platform} onValueChange={setPlatform}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="facebook">Facebook</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="content-type">Content Type</Label>
                <Select value={contentType} onValueChange={setContentType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="social_post">Social Post</SelectItem>
                    <SelectItem value="blog_draft">Blog Draft</SelectItem>
                    <SelectItem value="announcement">Announcement</SelectItem>
                    <SelectItem value="product_update">
                      Product Update
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={handleGenerateContent}
              disabled={!sourceMaterial.trim() || isGenerating}
              className="w-full">
              {isGenerating ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <PenTool className="h-4 w-4 mr-2" />
                  Generate Content
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Recent Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Recent Content
            </CardTitle>
          </CardHeader>
          <CardContent>
            {generatedContents.length === 0 ? (
              <div className="text-center py-8">
                <PenTool className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No content generated yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {generatedContents.slice(0, 5).map((content) => (
                  <div
                    key={content.content_id}
                    className="flex items-start justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedContent(content)}>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span>{getPlatformIcon(content.platform)}</span>
                        <p className="font-medium truncate">
                          {content.title ||
                            `${content.platform} ${content.content_type}`}
                        </p>
                      </div>
                      <p className="text-sm text-gray-500 truncate">
                        {content.content
                          ? content.content.substring(0, 100) + '...'
                          : 'No content preview available'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(content.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-3">
                      {getStatusBadge(content.status)}
                      <Button size="sm" variant="ghost">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Content Preview */}
      {selectedContent && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{getPlatformIcon(selectedContent.platform)}</span>
                <span>
                  {selectedContent.title ||
                    `${selectedContent.platform} Content`}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {getStatusBadge(selectedContent.status)}
                <Badge variant="outline">{selectedContent.content_type}</Badge>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Content Preview */}
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap">
                  {selectedContent.content}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Created: {new Date(selectedContent.created_at).toLocaleString()}
                {selectedContent.updated_at &&
                  selectedContent.updated_at !== selectedContent.created_at && (
                    <span>
                      {' '}
                      • Updated:{' '}
                      {new Date(selectedContent.updated_at).toLocaleString()}
                    </span>
                  )}
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(selectedContent.content)}>
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </Button>
                <Button size="sm" variant="outline">
                  <ThumbsUp className="h-4 w-4 mr-1" />
                  Approve
                </Button>
                <Button size="sm" variant="outline">
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button size="sm" variant="outline">
                  <Share className="h-4 w-4 mr-1" />
                  Share
                </Button>
              </div>
            </div>

            {/* Source Data */}
            {selectedContent.source_data && (
              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Generation Details</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Platform:</span>{' '}
                    {selectedContent.platform}
                  </div>
                  <div>
                    <span className="font-medium">Content Type:</span>{' '}
                    {selectedContent.content_type}
                  </div>
                  {selectedContent.source_data.brand_tone && (
                    <div>
                      <span className="font-medium">Brand Tone:</span>{' '}
                      {selectedContent.source_data.brand_tone}
                    </div>
                  )}
                  {selectedContent.source_data.target_audience && (
                    <div>
                      <span className="font-medium">Target Audience:</span>{' '}
                      {selectedContent.source_data.target_audience}
                    </div>
                  )}
                </div>
                {selectedContent.source_data.source_material && (
                  <div className="mt-3">
                    <span className="font-medium">Source Material:</span>
                    <div className="mt-1 p-3 bg-gray-100 rounded text-sm">
                      {selectedContent.source_data.source_material}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
