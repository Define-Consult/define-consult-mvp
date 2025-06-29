'use client';

import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  CreditCard,
  ArrowUpRight,
  Check,
  Zap,
  BarChart3,
  Calendar,
} from 'lucide-react';

export default function BillingPage() {
  const { data: session } = useSession();

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500">Please log in to access billing</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Billing & Usage</h1>
        <p className="text-gray-600 mt-1">
          Manage your subscription and monitor your usage
        </p>
      </div>

      {/* Current Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Current Plan
              </span>
              <Badge className="bg-blue-100 text-blue-700">Pro</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Monthly Cost</span>
                <span className="font-semibold text-lg">$49/month</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Next Billing Date</span>
                <span className="font-medium">January 15, 2025</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Credits Included</span>
                <span className="font-medium">10,000 / month</span>
              </div>
              <div className="pt-4 border-t">
                <Button className="w-full" variant="outline">
                  <ArrowUpRight className="h-4 w-4 mr-2" />
                  Manage Subscription
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Usage This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-2xl font-bold">3,247</div>
                <div className="text-sm text-gray-600">Credits Used</div>
              </div>
              <Progress value={32.47} className="w-full" />
              <div className="text-xs text-gray-500 text-center">
                32.47% of monthly allowance
              </div>
              <div className="text-center pt-2">
                <span className="text-sm font-medium text-green-600">
                  6,753 credits remaining
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Usage Breakdown */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Usage Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-2">1,247</div>
              <div className="text-sm text-gray-600 mb-2">User Whisperer</div>
              <div className="text-xs text-gray-500">Transcript Analysis</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-600 mb-2">892</div>
              <div className="text-sm text-gray-600 mb-2">Market Maven</div>
              <div className="text-xs text-gray-500">Competitor Monitoring</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-purple-600 mb-2">
                1,108
              </div>
              <div className="text-sm text-gray-600 mb-2">
                Narrative Architect
              </div>
              <div className="text-xs text-gray-500">Content Generation</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Available Plans */}
      <Card>
        <CardHeader>
          <CardTitle>Upgrade Your Plan</CardTitle>
          <p className="text-sm text-gray-600">
            Need more credits or features? Choose a plan that fits your needs.
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Starter Plan */}
            <div className="border rounded-lg p-6">
              <div className="text-center mb-4">
                <h3 className="font-semibold text-lg">Starter</h3>
                <div className="text-2xl font-bold mt-2">
                  $19<span className="text-sm text-gray-500">/month</span>
                </div>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  5,000 credits/month
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  All AI agents
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  Email support
                </li>
              </ul>
              <Button variant="outline" className="w-full mt-4">
                Downgrade
              </Button>
            </div>

            {/* Pro Plan (Current) */}
            <div className="border-2 border-blue-500 rounded-lg p-6 relative">
              <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                Current Plan
              </Badge>
              <div className="text-center mb-4">
                <h3 className="font-semibold text-lg">Pro</h3>
                <div className="text-2xl font-bold mt-2">
                  $49<span className="text-sm text-gray-500">/month</span>
                </div>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  10,000 credits/month
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  All AI agents
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  Priority support
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  Advanced analytics
                </li>
              </ul>
              <Button className="w-full mt-4" disabled>
                Current Plan
              </Button>
            </div>

            {/* Enterprise Plan */}
            <div className="border rounded-lg p-6">
              <div className="text-center mb-4">
                <h3 className="font-semibold text-lg">Enterprise</h3>
                <div className="text-2xl font-bold mt-2">
                  $99<span className="text-sm text-gray-500">/month</span>
                </div>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  25,000 credits/month
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  All AI agents
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  24/7 phone support
                </li>
                <li className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  Custom integrations
                </li>
              </ul>
              <Button className="w-full mt-4">Upgrade</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
