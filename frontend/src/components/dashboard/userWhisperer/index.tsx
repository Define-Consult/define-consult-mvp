'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Upload,
  Brain,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  Eye,
  Download,
  Trash2,
} from 'lucide-react';
import { userWhispererApi, type Transcript } from '@/lib/api/agents';

export default function UserWhispererComponent() {
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [selectedTranscript, setSelectedTranscript] =
    useState<Transcript | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [uploadTitle, setUploadTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Load transcripts
  const loadTranscripts = useCallback(async () => {
    setLoading(true);
    const response = await userWhispererApi.getTranscripts();
    if (response.success && response.data?.transcripts) {
      setTranscripts(response.data.transcripts);
    }
    setLoading(false);
  }, []);

  // Load transcript details
  const loadTranscriptDetails = useCallback(async (transcriptId: string) => {
    if (!transcriptId || transcriptId === 'undefined') {
      console.error('Invalid transcript ID:', transcriptId);
      return;
    }

    const response = await userWhispererApi.getTranscript(transcriptId);
    if (response.success) {
      setSelectedTranscript(response.data);
    }
  }, []);

  useEffect(() => {
    loadTranscripts();
  }, [loadTranscripts]);

  // Handle file upload
  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const response = await userWhispererApi.uploadTranscript(
        selectedFile,
        uploadTitle || 'Customer Feedback'
      );

      if (response.success) {
        setSelectedFile(null);
        setUploadTitle('');
        await loadTranscripts();

        // Start polling for completion
        if (response.data?.transcript_id) {
          pollTranscriptStatus(response.data.transcript_id);
        }
      } else {
        alert(`Upload failed: ${response.error}`);
      }
    } catch (error) {
      alert(`Upload error: ${error}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Poll transcript status
  const pollTranscriptStatus = useCallback(async (transcriptId: string) => {
    const maxAttempts = 30; // 30 attempts = 5 minutes
    let attempts = 0;

    const poll = async () => {
      attempts++;
      const response = await userWhispererApi.getTranscript(transcriptId);

      if (response.success) {
        const transcript = response.data;

        // Update the transcript in our list
        setTranscripts((prev) =>
          prev.map((t) => (t.id === transcriptId ? transcript : t))
        );

        if (
          transcript.status === 'completed' ||
          transcript.status === 'error'
        ) {
          return; // Stop polling
        }

        if (attempts < maxAttempts) {
          setTimeout(poll, 10000); // Poll every 10 seconds
        }
      }
    };

    setTimeout(poll, 5000); // Start polling after 5 seconds
  }, []);

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
      case 'uploaded':
        return (
          <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
            <Upload className="h-3 w-3 mr-1" />
            Uploaded
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
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
        <Brain className="h-6 w-6 text-blue-600" />
        <h2 className="text-2xl font-bold">User Whisperer</h2>
        <Badge variant="outline">Customer Feedback Analysis</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload Transcript
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Title (Optional)</Label>
              <Input
                id="title"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="Customer Interview #1"
              />
            </div>

            <div>
              <Label htmlFor="file">Transcript File</Label>
              <Input
                id="file"
                type="file"
                accept=".txt,.md,.docx"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
              <p className="text-sm text-gray-500 mt-1">
                Supports .txt, .md, and .docx files
              </p>
            </div>

            <Button
              onClick={handleFileUpload}
              disabled={!selectedFile || isUploading}
              className="w-full">
              {isUploading ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Uploading & Processing...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload & Analyze
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Transcripts List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Transcripts
            </CardTitle>
          </CardHeader>
          <CardContent>
            {transcripts.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No transcripts uploaded yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {transcripts.slice(0, 5).map((transcript) => (
                  <div
                    key={transcript.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => loadTranscriptDetails(transcript.id)}>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{transcript.title}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(transcript.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(transcript.status)}
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

      {/* Transcript Details */}
      {selectedTranscript && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{selectedTranscript.title}</span>
              {getStatusBadge(selectedTranscript.status)}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {selectedTranscript.status === 'completed' &&
            selectedTranscript.analysis ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Insights */}
                <div>
                  <h4 className="font-semibold mb-3">Key Insights</h4>
                  <div className="space-y-2">
                    {selectedTranscript.insights?.map((insight, index) => (
                      <div
                        key={`insight-${index}`}
                        className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pain Points */}
                <div>
                  <h4 className="font-semibold mb-3">Pain Points</h4>
                  <div className="space-y-2">
                    {selectedTranscript.pain_points?.map((point, index) => (
                      <div
                        key={`pain-point-${index}`}
                        className="p-3 bg-red-50 rounded-lg">
                        <p className="text-sm">{point}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key Themes */}
                <div>
                  <h4 className="font-semibold mb-3">Key Themes</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedTranscript.key_themes?.map((theme, index) => (
                      <Badge key={`theme-${index}`} variant="outline">
                        {theme}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Feature Requests */}
                <div>
                  <h4 className="font-semibold mb-3">Feature Requests</h4>
                  <div className="space-y-2">
                    {selectedTranscript.feature_requests?.map(
                      (request, index) => (
                        <div
                          key={`feature-request-${index}`}
                          className="p-3 bg-green-50 rounded-lg">
                          <p className="text-sm">{request}</p>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* Sentiment Score */}
                {selectedTranscript.sentiment_score !== undefined && (
                  <div className="md:col-span-2">
                    <h4 className="font-semibold mb-3">Sentiment Analysis</h4>
                    <div className="flex items-center gap-4">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${
                            selectedTranscript.sentiment_score > 0.5
                              ? 'bg-green-500'
                              : selectedTranscript.sentiment_score > 0
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{
                            width: `${
                              Math.abs(selectedTranscript.sentiment_score) * 100
                            }%`,
                          }}></div>
                      </div>
                      <span className="font-medium">
                        {selectedTranscript.sentiment_score > 0.5
                          ? 'Positive'
                          : selectedTranscript.sentiment_score > 0
                          ? 'Neutral'
                          : 'Negative'}
                      </span>
                      <span className="text-sm text-gray-500">
                        ({selectedTranscript.sentiment_score.toFixed(2)})
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ) : selectedTranscript.status === 'processing' ? (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-spin" />
                <h3 className="text-lg font-semibold mb-2">
                  Processing Transcript
                </h3>
                <p className="text-gray-500">
                  AI is analyzing your customer feedback. This may take a few
                  minutes.
                </p>
              </div>
            ) : selectedTranscript.status === 'error' ? (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Processing Error</h3>
                <p className="text-gray-500">
                  There was an error processing this transcript. Please try
                  uploading again.
                </p>
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  Transcript Uploaded
                </h3>
                <p className="text-gray-500">Processing will begin shortly.</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
