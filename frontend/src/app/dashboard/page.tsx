'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Brain,
  TrendingUp,
  PenTool,
  BarChart3,
  Settings,
  Users,
  ArrowRight,
  Plus,
} from 'lucide-react';

import AIActionCenter from '@/components/dashboard/aiActionCenter';
import DashboardLayout from '@/components/layout/DashboardLayout';

export default function DashboardPage() {
  const { data: session } = useSession();

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500">Please log in to access the dashboard</p>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Welcome back, {session.user?.email}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <Link href="/agents/user-whisperer">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Brain className="h-6 w-6 text-blue-600" />
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                </div>
                <h3 className="font-semibold text-lg mb-2">User Whisperer</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Analyze customer feedback and extract actionable insights
                </p>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    Upload & Analyze
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    PRD Generation
                  </Badge>
                </div>
              </CardContent>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <Link href="/agents/market-maven">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                </div>
                <h3 className="font-semibold text-lg mb-2">Market Maven</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Monitor competitors and track market trends
                </p>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    Competitor Analysis
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    Market Monitoring
                  </Badge>
                </div>
              </CardContent>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <Link href="/agents/narrative-architect">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <PenTool className="h-6 w-6 text-purple-600" />
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                </div>
                <h3 className="font-semibold text-lg mb-2">
                  Narrative Architect
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Generate compelling content for marketing campaigns
                </p>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    Content Generation
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    Multi-Platform
                  </Badge>
                </div>
              </CardContent>
            </Link>
          </Card>
        </div>

        {/* AI Action Center */}
        <AIActionCenter />

        {/* Additional Widgets */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Usage Analytics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">API Calls Today</span>
                  <span className="font-semibold">1,247</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Credits Used</span>
                  <span className="font-semibold">324 / 1,000</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: '32.4%' }}></div>
                </div>
                <Button variant="outline" className="w-full text-sm">
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Team Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600">
                      JD
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      John uploaded a transcript
                    </p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-green-600">
                      SM
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      Sarah added a competitor
                    </p>
                    <p className="text-xs text-gray-500">4 hours ago</p>
                  </div>
                </div>
                <Button variant="outline" className="w-full text-sm">
                  View All Activity
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Links</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Link href="/billing" className="block">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm">
                    Billing & Usage
                  </Button>
                </Link>
                <Link href="/settings" className="block">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm">
                    Account Settings
                  </Button>
                </Link>
                <Link href="/settings/integrations" className="block">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm">
                    Integrations
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  className="w-full justify-start text-sm">
                  Help & Support
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
