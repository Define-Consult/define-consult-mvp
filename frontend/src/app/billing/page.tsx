'use client';

import { useSession } from 'next-auth/react';
import DashboardLayout from '@/components/layout/DashboardLayout';
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
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  useBillingPlans,
  useBillingUsage,
  useCreateCheckoutSession,
  useManageSubscription,
} from '@/hooks/useProfile';

export default function BillingPage() {
  const { data: session } = useSession();
  const {
    data: plans,
    isLoading: plansLoading,
    error: plansError,
  } = useBillingPlans();
  const {
    data: usage,
    isLoading: usageLoading,
    error: usageError,
  } = useBillingUsage();
  const createCheckoutMutation = useCreateCheckoutSession();
  const manageSubscriptionMutation = useManageSubscription();

  const handleUpgrade = (planId: string) => {
    const successUrl = `${window.location.origin}/billing?success=true`;
    const cancelUrl = `${window.location.origin}/billing?canceled=true`;

    createCheckoutMutation.mutate({
      planId,
      successUrl,
      cancelUrl,
    });
  };

  const handleManageSubscription = () => {
    manageSubscriptionMutation.mutate();
  };

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500">Please log in to access billing</p>
        </div>
      </div>
    );
  }

  if (plansLoading || usageLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading billing information...</span>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (plansError || usageError) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              Failed to load billing information
            </h3>
            <p className="text-gray-600">Please try refreshing the page</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const currentPlan =
    plans?.find(
      (plan) => plan.name.toLowerCase() === usage?.current_plan.toLowerCase()
    ) || plans?.[0];
  const usagePercentage = usage
    ? (usage.agent_actions_used / usage.agent_actions_limit) * 100
    : 0;

  return (
    <DashboardLayout>
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
                <Badge className="bg-blue-100 text-blue-700">
                  {usage?.current_plan || 'Free'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Monthly Cost</span>
                  <span className="font-semibold text-lg">
                    ${currentPlan?.price_usd_per_month || 0}/month
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Billing Period</span>
                  <span className="font-medium">
                    {usage
                      ? new Date(
                          usage.billing_period_start
                        ).toLocaleDateString()
                      : 'N/A'}{' '}
                    -
                    {usage
                      ? new Date(usage.billing_period_end).toLocaleDateString()
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    Agent Actions Included
                  </span>
                  <span className="font-medium">
                    {usage?.agent_actions_limit.toLocaleString() || 0} / month
                  </span>
                </div>
                <div className="pt-4 border-t">
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={handleManageSubscription}
                    disabled={manageSubscriptionMutation.isPending}>
                    {manageSubscriptionMutation.isPending ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <ArrowUpRight className="h-4 w-4 mr-2" />
                    )}
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
                  <div className="text-2xl font-bold">
                    {usage?.agent_actions_used.toLocaleString() || 0}
                  </div>
                  <div className="text-sm text-gray-600">
                    Agent Actions Used
                  </div>
                </div>
                <Progress value={usagePercentage} className="w-full" />
                <div className="text-xs text-gray-500 text-center">
                  {usagePercentage.toFixed(1)}% of monthly allowance
                </div>
                <div className="text-center pt-2">
                  <span
                    className={`text-sm font-medium ${
                      usagePercentage > 80 ? 'text-red-600' : 'text-green-600'
                    }`}>
                    {(
                      (usage?.agent_actions_limit || 0) -
                      (usage?.agent_actions_used || 0)
                    ).toLocaleString()}{' '}
                    actions remaining
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Available Plans */}
        <Card>
          <CardHeader>
            <CardTitle>Available Plans</CardTitle>
            <p className="text-sm text-gray-600">
              Choose a plan that fits your needs. Upgrade or downgrade anytime.
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {plans?.map((plan) => {
                const isCurrentPlan =
                  plan.name.toLowerCase() === usage?.current_plan.toLowerCase();

                return (
                  <div
                    key={plan.id}
                    className={`border rounded-lg p-6 relative ${
                      isCurrentPlan ? 'border-2 border-blue-500' : ''
                    }`}>
                    {isCurrentPlan && (
                      <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                        Current Plan
                      </Badge>
                    )}

                    <div className="text-center mb-4">
                      <h3 className="font-semibold text-lg">{plan.name}</h3>
                      <div className="text-2xl font-bold mt-2">
                        ${plan.price_usd_per_month}
                        <span className="text-sm text-gray-500">/month</span>
                      </div>
                    </div>

                    <ul className="space-y-2 text-sm mb-6">
                      <li className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        {plan.monthly_agent_action_limit.toLocaleString()} agent
                        actions/month
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        All AI agents included
                      </li>
                      {plan.priority_support && (
                        <li className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-500" />
                          Priority support
                        </li>
                      )}
                      {plan.is_team_plan && (
                        <li className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-500" />
                          Team collaboration
                        </li>
                      )}
                      {plan.available_integrations.length > 0 && (
                        <li className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-500" />
                          {plan.available_integrations.length} integrations
                        </li>
                      )}
                    </ul>

                    <Button
                      className="w-full"
                      variant={isCurrentPlan ? 'outline' : 'default'}
                      disabled={
                        isCurrentPlan || createCheckoutMutation.isPending
                      }
                      onClick={() => !isCurrentPlan && handleUpgrade(plan.id)}>
                      {createCheckoutMutation.isPending ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : null}
                      {isCurrentPlan
                        ? 'Current Plan'
                        : plan.price_usd_per_month === 0
                        ? 'Downgrade'
                        : 'Upgrade'}
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
