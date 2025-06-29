'use client';

import { signOut, useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Mail,
  CheckCircle,
  ExternalLink,
  LogOut,
  Settings,
  User,
  Brain,
  TrendingUp,
  PenTool,
  Home,
} from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import AIActionCenter from '@/components/dashboard/aiActionCenter';
import UserWhispererComponent from '@/components/dashboard/userWhisperer';
import MarketMavenComponent from '@/components/dashboard/marketMaven';
import NarrativeArchitectComponent from '@/components/dashboard/narrativeArchitect';

export default function UserDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [imageError, setImageError] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  const handleLogout = async () => {
    try {
      // Clear any client-side state before logout
      setImageError(false);

      await signOut({
        callbackUrl: '/login',
        redirect: true,
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Force redirect if signOut fails
      window.location.href = '/login';
    }
  };

  const handleResendVerification = async () => {
    // TODO: Connect this to our FastAPI backend to send the email via AWS SES
    // Example: await fetch('/api/v1/send-verification-email', { method: 'POST', body: JSON.stringify({ email: session.user.email }) });
    alert(
      'Sending verification email via backend... (Functionality to be implemented)'
    );
  };

  // Show loading state while checking authentication
  if (status === 'loading') {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-8 md:p-24 bg-dc-white text-dc-black font-sans">
        <div className="flex flex-col items-center justify-center text-center max-w-xl w-full">
          <Image
            src="/define-consult-logo.png"
            alt="Define Consult Logo"
            width={60}
            height={60}
            priority
            className="mb-6"
          />
          <Card className="bg-dc-white text-dc-black border-dc-gray-200 shadow-lg rounded-xl w-full">
            <CardContent className="p-6 flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-dc-black"></div>
              <p className="text-dc-gray">Loading your dashboard...</p>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  // Don't render anything until mounted
  if (!mounted) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-8 md:p-24 bg-dc-white text-dc-black font-sans">
        <div className="flex flex-col items-center justify-center text-center max-w-xl w-full">
          <Image
            src="/define-consult-logo.png"
            alt="Define Consult Logo"
            width={60}
            height={60}
            priority
            className="mb-6"
          />
          <Card className="bg-dc-white text-dc-black border-dc-gray-200 shadow-lg rounded-xl w-full">
            <CardContent className="p-6 flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-dc-black"></div>
              <p className="text-dc-gray">Loading your dashboard...</p>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  // Don't render anything if not authenticated (prevents flash)
  if (status === 'unauthenticated') {
    return null;
  }

  // Only render dashboard if we have a valid session
  if (!session?.user) {
    return null;
  }

  return (
    <div className="flex flex-col min-h-screen bg-dc-white text-dc-black font-sans">
      {/* Top Navigation Header */}
      <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-dc-white/90 backdrop-blur-md shadow-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo and Project Name */}
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="flex items-center gap-2">
              <Image
                src="/define-consult-logo.png"
                alt="Define Consult Logo"
                width={36}
                height={36}
                className="drop-shadow-sm"
              />
              <span className="text-xl font-bold tracking-tight hidden sm:block">
                Define Consult
              </span>
            </Link>
          </div>

          {/* User Profile and Dropdown Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              {/* This Button now has `p-0` to remove padding that was hiding the avatar */}
              <Button
                variant="ghost"
                className="relative h-10 w-10 rounded-full focus-visible:ring-offset-0 focus-visible:ring-0 p-0">
                {/* Avatar Image or Fallback */}
                {session.user.image && !imageError ? (
                  <Image
                    src={session.user.image || '/placeholder.svg'}
                    alt="Profile"
                    width={40}
                    height={40}
                    className="rounded-full border-2 border-dc-gray-200 shadow-sm"
                    onError={() => setImageError(true)}
                  />
                ) : (
                  <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-dc-black font-bold border-2 border-dc-gray-200">
                    {(session.user.name || session.user.email || 'U')
                      .charAt(0)
                      .toUpperCase()}
                  </div>
                )}
                {/* Optional verification badge */}
                {session.user.emailVerified && (
                  <CheckCircle className="absolute bottom-0 right-0 w-4 h-4 text-green-500 bg-white rounded-full border border-white" />
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {session.user.name || 'User'}
                  </p>
                  <p className="text-xs leading-none text-dc-gray">
                    {session.user.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLogout}
                className="cursor-pointer text-red-600 hover:text-red-700">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 container mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <section className="space-y-4">
            <h1 className="text-3xl sm:text-4xl font-bold text-dc-black tracking-tight">
              Welcome back, {session.user.name || 'User'}!
            </h1>
            <p className="text-lg text-dc-gray max-w-2xl">
              Access your AI agents to analyze customer feedback, track
              competitors, and generate content.
            </p>

            {/* Email Verification Status Banner */}
            {session.user.emailVerified === false && (
              <Alert className="bg-amber-50 text-amber-800 border border-amber-200 shadow-sm rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <Mail className="h-6 w-6 text-amber-600 flex-shrink-0" />
                <div className="flex-1 space-y-1">
                  <AlertTitle className="text-base font-semibold">
                    Please verify your email
                  </AlertTitle>
                  <AlertDescription className="text-sm">
                    A verification link has been sent to {session.user.email}.
                    Please check your inbox.
                  </AlertDescription>
                </div>
                <Button
                  variant="outline"
                  onClick={handleResendVerification}
                  className="flex-shrink-0 w-full sm:w-auto border-amber-300 text-amber-700 hover:bg-amber-100">
                  Resend Email
                </Button>
              </Alert>
            )}
          </section>

          {/* Tabbed Interface for AI Agents */}
          <section className="space-y-6">
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger
                  value="overview"
                  className="flex items-center gap-2">
                  <Home className="h-4 w-4" />
                  <span className="hidden sm:inline">Overview</span>
                </TabsTrigger>
                <TabsTrigger
                  value="user-whisperer"
                  className="flex items-center gap-2">
                  <Brain className="h-4 w-4" />
                  <span className="hidden sm:inline">User Whisperer</span>
                </TabsTrigger>
                <TabsTrigger
                  value="market-maven"
                  className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  <span className="hidden sm:inline">Market Maven</span>
                </TabsTrigger>
                <TabsTrigger
                  value="narrative-architect"
                  className="flex items-center gap-2">
                  <PenTool className="h-4 w-4" />
                  <span className="hidden sm:inline">Narrative Architect</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div className="space-y-6">
                  {/* AI Action Center Overview */}
                  <AIActionCenter />

                  {/* Quick Actions */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card
                      className="cursor-pointer transition-all hover:shadow-lg"
                      onClick={() => setActiveTab('user-whisperer')}>
                      <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <Brain className="h-5 w-5 text-blue-600" />
                          User Whisperer
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-dc-gray mb-4">
                          Upload and analyze customer feedback transcripts
                        </p>
                        <Button variant="outline" className="w-full">
                          Analyze Transcripts
                        </Button>
                      </CardContent>
                    </Card>

                    <Card
                      className="cursor-pointer transition-all hover:shadow-lg"
                      onClick={() => setActiveTab('market-maven')}>
                      <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <TrendingUp className="h-5 w-5 text-green-600" />
                          Market Maven
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-dc-gray mb-4">
                          Track competitors and analyze market trends
                        </p>
                        <Button variant="outline" className="w-full">
                          Analyze Competitors
                        </Button>
                      </CardContent>
                    </Card>

                    <Card
                      className="cursor-pointer transition-all hover:shadow-lg"
                      onClick={() => setActiveTab('narrative-architect')}>
                      <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <PenTool className="h-5 w-5 text-purple-600" />
                          Narrative Architect
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-dc-gray mb-4">
                          Generate marketing content and copy
                        </p>
                        <Button variant="outline" className="w-full">
                          Generate Content
                        </Button>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Account Information */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <User className="h-5 w-5" />
                        Account Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-dc-gray">Email:</span>
                        <span className="font-semibold">
                          {session.user.email}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-dc-gray">
                          Status:
                        </span>
                        <span
                          className={`font-semibold ${
                            session.user.emailVerified
                              ? 'text-green-600'
                              : 'text-red-500'
                          }`}>
                          {session.user.emailVerified
                            ? 'Verified'
                            : 'Unverified'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-dc-gray">
                          User ID:
                        </span>
                        <span className="font-mono text-dc-black text-xs break-all">
                          {session.user.id}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="user-whisperer">
                <UserWhispererComponent />
              </TabsContent>

              <TabsContent value="market-maven">
                <MarketMavenComponent />
              </TabsContent>

              <TabsContent value="narrative-architect">
                <NarrativeArchitectComponent />
              </TabsContent>
            </Tabs>
          </section>
        </div>
      </main>
    </div>
  );
}
