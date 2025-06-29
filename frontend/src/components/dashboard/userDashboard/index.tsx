'use client';

import { signOut, useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Mail,
  CheckCircle,
  ExternalLink,
  LogOut,
  Settings,
  User,
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

export default function UserDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [imageError, setImageError] = useState(false);
  const [mounted, setMounted] = useState(false);

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
      <main className="flex-1 container mx-auto px-6 py-12 md:py-16">
        <div className="space-y-10">
          {/* Welcome and Verification Section */}
          <section className="space-y-6">
            <h1 className="text-4xl sm:text-5xl font-extrabold text-dc-black tracking-tighter">
              Welcome back, {session.user.name || 'User'}!
            </h1>
            <p className="text-lg text-dc-gray max-w-2xl">
              This is your personal dashboard. Here you can manage your account
              and access all your tools.
            </p>

            {/* Email Verification Status Banner */}
            {session.user.emailVerified === false && (
              <Alert className="bg-gray-50 text-dc-black border border-gray-200 shadow-sm rounded-xl p-6 flex flex-col sm:flex-row items-start sm:items-center gap-4 transition-all duration-300">
                <Mail className="h-8 w-8 text-dc-black flex-shrink-0" />
                <div className="flex-1 space-y-1">
                  <AlertTitle className="text-lg font-bold">
                    Please verify your email.
                  </AlertTitle>
                  <AlertDescription className="text-sm text-dc-gray">
                    A verification link has been sent to **{session.user.email}
                    **. Please check your inbox to activate your account.
                  </AlertDescription>
                </div>
                <Button
                  variant="outline"
                  onClick={handleResendVerification}
                  className="flex-shrink-0 w-full sm:w-auto mt-4 sm:mt-0 bg-dc-white text-dc-black border border-dc-black hover:bg-gray-100 transition-colors">
                  Resend Email
                </Button>
              </Alert>
            )}
          </section>

          {/* AI Action Center - Main Feature */}
          <section className="space-y-6">
            <AIActionCenter />
          </section>

          {/* Account Management Section */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Account Information Card */}
            <Card className="bg-dc-white border-dc-gray-200 shadow-lg rounded-2xl p-6 transition-transform transform hover:scale-[1.01] hover:shadow-2xl">
              <CardHeader className="p-0 mb-4">
                <CardTitle className="text-2xl font-bold">Account</CardTitle>
              </CardHeader>
              <CardContent className="p-0 space-y-4">
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-dc-gray">Email:</span>
                    <span className="font-semibold">{session.user.email}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-dc-gray">Status:</span>
                    <span
                      className={`font-semibold ${
                        session.user.emailVerified
                          ? 'text-green-600'
                          : 'text-red-500'
                      }`}>
                      {session.user.emailVerified ? 'Verified' : 'Unverified'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-dc-gray">User ID:</span>
                    <span className="font-mono text-dc-black text-xs break-all">
                      {session.user.id}
                    </span>
                  </div>
                </div>
                <Button
                  variant="outline"
                  className="w-full h-12 bg-dc-white border border-dc-black hover:bg-gray-100 text-dc-black font-semibold rounded-lg transition-colors">
                  <Settings size={20} className="mr-2" />
                  Manage Profile
                </Button>
              </CardContent>
            </Card>

            {/* Other Action Cards */}
            <Card className="bg-dc-white border-dc-gray-200 shadow-lg rounded-2xl p-6 transition-transform transform hover:scale-[1.01] hover:shadow-2xl">
              <CardHeader className="p-0 mb-4">
                <CardTitle className="text-2xl font-bold">Product</CardTitle>
              </CardHeader>
              <CardContent className="p-0 space-y-4">
                <p className="text-sm text-dc-gray">
                  Explore new features and integrations to boost your workflow.
                </p>
                <Button className="w-full h-12 bg-dc-black hover:bg-gray-800 text-dc-white font-semibold rounded-lg transition-colors">
                  Go to AI Co-Pilot
                  <ExternalLink size={18} className="ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-dc-white border-dc-gray-200 shadow-lg rounded-2xl p-6 transition-transform transform hover:scale-[1.01] hover:shadow-2xl">
              <CardHeader className="p-0 mb-4">
                <CardTitle className="text-2xl font-bold">Support</CardTitle>
              </CardHeader>
              <CardContent className="p-0 space-y-4">
                <p className="text-sm text-dc-gray">
                  Need help? Contact our support team or check the
                  documentation.
                </p>
                <Button
                  variant="outline"
                  className="w-full h-12 bg-dc-white border border-dc-black hover:bg-gray-100 text-dc-black font-semibold rounded-lg transition-colors">
                  Contact Support
                </Button>
              </CardContent>
            </Card>
          </section>

          {/* Placeholder for future features */}
          <section className="pt-6">
            <div className="text-center pt-8 border-t border-dc-gray-200">
              <p className="text-sm text-dc-gray">
                More features are coming soon!
              </p>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
