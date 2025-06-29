'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  User,
  Bell,
  Plug,
  Shield,
  Save,
  Mail,
  Smartphone,
  Globe,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  useProfile,
  useUpdateProfile,
  useDeleteAccount,
} from '@/hooks/useProfile';
import { useAppStore } from '@/stores/appStore';

export default function SettingsPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const { data: profile, isLoading, error } = useProfile();
  const updateProfileMutation = useUpdateProfile();
  const deleteAccountMutation = useDeleteAccount();

  // Local form state
  const [profileForm, setProfileForm] = useState({
    name: '',
    company_name: '',
    role_at_company: '',
    industry: '',
    linkedin_profile_url: '',
  });

  const [notificationPreferences, setNotificationPreferences] = useState({
    email_digest: true,
    slack_alerts: false,
    in_app_notifications: true,
    marketing_emails: false,
  });

  const [brandTonePreferences, setBrandTonePreferences] = useState({
    formal: 0.5,
    friendly: 0.5,
    professional: 0.5,
    creative: 0.5,
  });

  // Update form state when profile data is loaded
  useEffect(() => {
    if (profile) {
      setProfileForm({
        name: profile.name || '',
        company_name: profile.company_name || '',
        role_at_company: profile.role_at_company || '',
        industry: profile.industry || '',
        linkedin_profile_url: profile.linkedin_profile_url || '',
      });

      if (profile.notification_preferences) {
        setNotificationPreferences({
          email_digest: profile.notification_preferences.email_digest ?? true,
          slack_alerts: profile.notification_preferences.slack_alerts ?? false,
          in_app_notifications:
            profile.notification_preferences.in_app_notifications ?? true,
          marketing_emails:
            profile.notification_preferences.marketing_emails ?? false,
        });
      }

      if (profile.brand_tone_preferences) {
        setBrandTonePreferences({
          formal: profile.brand_tone_preferences.formal ?? 0.5,
          friendly: profile.brand_tone_preferences.friendly ?? 0.5,
          professional: profile.brand_tone_preferences.professional ?? 0.5,
          creative: profile.brand_tone_preferences.creative ?? 0.5,
        });
      }
    }
  }, [profile]);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate({
      ...profileForm,
      notification_preferences: notificationPreferences,
      brand_tone_preferences: brandTonePreferences,
    });
  };

  const handleDeleteAccount = async () => {
    deleteAccountMutation.mutate(undefined, {
      onSuccess: () => {
        router.push('/login');
      },
    });
  };

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500">Please log in to access settings</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading settings...</span>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              Failed to load settings
            </h3>
            <p className="text-gray-600">Please try refreshing the page</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">
            Manage your account preferences and integrations
          </p>
        </div>

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Profile
            </TabsTrigger>
            <TabsTrigger
              value="notifications"
              className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger
              value="integrations"
              className="flex items-center gap-2">
              <Plug className="h-4 w-4" />
              Integrations
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Security
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <form onSubmit={handleProfileSubmit}>
              <Card>
                <CardHeader>
                  <CardTitle>Profile Information</CardTitle>
                  <p className="text-sm text-gray-600">
                    Update your personal information and preferences
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={profileForm.name}
                      onChange={(e) =>
                        setProfileForm((prev) => ({
                          ...prev,
                          name: e.target.value,
                        }))
                      }
                      placeholder="John Doe"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={session.user?.email || profile?.email || ''}
                      disabled
                    />
                    <p className="text-xs text-gray-500">
                      Email address cannot be changed
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="company">Company</Label>
                    <Input
                      id="company"
                      value={profileForm.company_name}
                      onChange={(e) =>
                        setProfileForm((prev) => ({
                          ...prev,
                          company_name: e.target.value,
                        }))
                      }
                      placeholder="Acme Inc."
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Input
                      id="role"
                      value={profileForm.role_at_company}
                      onChange={(e) =>
                        setProfileForm((prev) => ({
                          ...prev,
                          role_at_company: e.target.value,
                        }))
                      }
                      placeholder="Product Manager"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="industry">Industry</Label>
                    <Input
                      id="industry"
                      value={profileForm.industry}
                      onChange={(e) =>
                        setProfileForm((prev) => ({
                          ...prev,
                          industry: e.target.value,
                        }))
                      }
                      placeholder="SaaS"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="linkedin">LinkedIn Profile URL</Label>
                    <Input
                      id="linkedin"
                      value={profileForm.linkedin_profile_url}
                      onChange={(e) =>
                        setProfileForm((prev) => ({
                          ...prev,
                          linkedin_profile_url: e.target.value,
                        }))
                      }
                      placeholder="https://linkedin.com/in/johndoe"
                    />
                  </div>

                  {/* Brand Tone Preferences */}
                  <div className="space-y-4">
                    <div>
                      <Label className="text-base font-semibold">
                        Brand Tone Preferences
                      </Label>
                      <p className="text-sm text-gray-600">
                        Adjust these sliders to define your preferred content
                        tone for AI-generated content
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="formal">
                          Formal ({brandTonePreferences.formal.toFixed(1)})
                        </Label>
                        <input
                          id="formal"
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={brandTonePreferences.formal}
                          onChange={(e) =>
                            setBrandTonePreferences((prev) => ({
                              ...prev,
                              formal: parseFloat(e.target.value),
                            }))
                          }
                          className="w-full"
                        />
                      </div>
                      <div>
                        <Label htmlFor="friendly">
                          Friendly ({brandTonePreferences.friendly.toFixed(1)})
                        </Label>
                        <input
                          id="friendly"
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={brandTonePreferences.friendly}
                          onChange={(e) =>
                            setBrandTonePreferences((prev) => ({
                              ...prev,
                              friendly: parseFloat(e.target.value),
                            }))
                          }
                          className="w-full"
                        />
                      </div>
                      <div>
                        <Label htmlFor="professional">
                          Professional (
                          {brandTonePreferences.professional.toFixed(1)})
                        </Label>
                        <input
                          id="professional"
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={brandTonePreferences.professional}
                          onChange={(e) =>
                            setBrandTonePreferences((prev) => ({
                              ...prev,
                              professional: parseFloat(e.target.value),
                            }))
                          }
                          className="w-full"
                        />
                      </div>
                      <div>
                        <Label htmlFor="creative">
                          Creative ({brandTonePreferences.creative.toFixed(1)})
                        </Label>
                        <input
                          id="creative"
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={brandTonePreferences.creative}
                          onChange={(e) =>
                            setBrandTonePreferences((prev) => ({
                              ...prev,
                              creative: parseFloat(e.target.value),
                            }))
                          }
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="flex items-center gap-2"
                    disabled={updateProfileMutation.isPending}>
                    {updateProfileMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Save Changes
                  </Button>
                </CardContent>
              </Card>
            </form>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <p className="text-sm text-gray-600">
                  Choose how you want to be notified about important updates
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Mail className="h-5 w-5 text-gray-500" />
                      <div>
                        <Label className="text-base">Email Digest</Label>
                        <p className="text-sm text-gray-500">
                          Receive daily/weekly summaries via email
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={notificationPreferences.email_digest}
                      onCheckedChange={(checked) =>
                        setNotificationPreferences((prev) => ({
                          ...prev,
                          email_digest: checked,
                        }))
                      }
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Smartphone className="h-5 w-5 text-gray-500" />
                      <div>
                        <Label className="text-base">
                          In-App Notifications
                        </Label>
                        <p className="text-sm text-gray-500">
                          Show notifications within the application
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={notificationPreferences.in_app_notifications}
                      onCheckedChange={(checked) =>
                        setNotificationPreferences((prev) => ({
                          ...prev,
                          in_app_notifications: checked,
                        }))
                      }
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Globe className="h-5 w-5 text-gray-500" />
                      <div>
                        <Label className="text-base">Slack Alerts</Label>
                        <p className="text-sm text-gray-500">
                          Send notifications to your connected Slack workspace
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={notificationPreferences.slack_alerts}
                      onCheckedChange={(checked) =>
                        setNotificationPreferences((prev) => ({
                          ...prev,
                          slack_alerts: checked,
                        }))
                      }
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Mail className="h-5 w-5 text-gray-500" />
                      <div>
                        <Label className="text-base">
                          Marketing Communications
                        </Label>
                        <p className="text-sm text-gray-500">
                          Receive updates about new features and promotions
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={notificationPreferences.marketing_emails}
                      onCheckedChange={(checked) =>
                        setNotificationPreferences((prev) => ({
                          ...prev,
                          marketing_emails: checked,
                        }))
                      }
                    />
                  </div>
                </div>

                <Button
                  onClick={handleProfileSubmit}
                  className="flex items-center gap-2"
                  disabled={updateProfileMutation.isPending}>
                  {updateProfileMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Save className="h-4 w-4" />
                  )}
                  Save Preferences
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Integrations Tab */}
          <TabsContent value="integrations">
            <Card>
              <CardHeader>
                <CardTitle>Integrations</CardTitle>
                <p className="text-sm text-gray-600">
                  Connect with external services and tools
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold">Slack</h4>
                        <Switch />
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        Send notifications to your Slack workspace
                      </p>
                      <Button variant="outline" size="sm" className="w-full">
                        Configure
                      </Button>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold">Discord</h4>
                        <Switch />
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        Post updates to your Discord server
                      </p>
                      <Button variant="outline" size="sm" className="w-full">
                        Configure
                      </Button>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold">Zapier</h4>
                        <Switch />
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        Automate workflows with 5000+ apps
                      </p>
                      <Button variant="outline" size="sm" className="w-full">
                        Configure
                      </Button>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold">Webhook</h4>
                        <Switch />
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        Send data to custom endpoints
                      </p>
                      <Button variant="outline" size="sm" className="w-full">
                        Configure
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <p className="text-sm text-gray-600">
                  Manage your account security and access
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div>
                    <Label className="text-base font-semibold">
                      Password Management
                    </Label>
                    <p className="text-sm text-gray-600 mb-3">
                      Password is managed through your authentication provider
                      (Google, etc.)
                    </p>
                    <Badge variant="outline">Managed externally</Badge>
                  </div>

                  <Separator />

                  <div>
                    <Label className="text-base font-semibold">
                      Two-Factor Authentication
                    </Label>
                    <p className="text-sm text-gray-600 mb-3">
                      Add an extra layer of security to your account
                    </p>
                    <Button variant="outline" size="sm">
                      Manage 2FA
                    </Button>
                  </div>

                  <Separator />

                  <div>
                    <Label className="text-base font-semibold">API Keys</Label>
                    <p className="text-sm text-gray-600 mb-3">
                      Manage API keys for programmatic access
                    </p>
                    <Button variant="outline" size="sm">
                      Manage API Keys
                    </Button>
                  </div>

                  <Separator />

                  <div>
                    <Label className="text-base font-semibold">
                      Data Export
                    </Label>
                    <p className="text-sm text-gray-600 mb-3">
                      Download all your data in machine-readable format
                    </p>
                    <Button variant="outline" size="sm">
                      Export Data
                    </Button>
                  </div>

                  <Separator />

                  <div>
                    <Label className="text-base font-semibold text-red-600">
                      Danger Zone
                    </Label>
                    <p className="text-sm text-gray-600 mb-3">
                      Irreversible and destructive actions
                    </p>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="destructive" size="sm">
                          Delete Account
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Are you absolutely sure?
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            This action cannot be undone. This will permanently
                            delete your account and remove all your data from
                            our servers, including:
                            <ul className="list-disc list-inside mt-2 space-y-1">
                              <li>All AI agent configurations</li>
                              <li>Generated content and insights</li>
                              <li>Usage history and analytics</li>
                              <li>Team memberships and data</li>
                            </ul>
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={handleDeleteAccount}
                            className="bg-red-600 hover:bg-red-700"
                            disabled={deleteAccountMutation.isPending}>
                            {deleteAccountMutation.isPending ? (
                              <>
                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                Deleting...
                              </>
                            ) : (
                              <>
                                <AlertTriangle className="h-4 w-4 mr-2" />
                                Delete Account
                              </>
                            )}
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
