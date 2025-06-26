'use client';

import Link from 'next/link';
import { signIn, useSession } from 'next-auth/react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/firebase/client';
import {
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
} from 'firebase/auth';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginForm() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (status === 'authenticated') {
      router.push('/dashboard');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className="flex flex-col gap-6 w-full max-w-md mx-auto">
        <Card className="bg-dc-white text-dc-black border-gray-200 shadow-lg rounded-xl">
          <CardContent className="p-6">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === 'authenticated') {
    return null;
  }

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      });

      if (result?.ok && !result?.error) {
        toast.success('Successfully logged in! Redirecting to dashboard...');
        router.push('/dashboard');
        router.refresh();
      } else {
        setError('Invalid email or password. Please try again.');
        toast.error('Login failed. Please check your credentials.');
      }
    } catch (err: any) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Login error:', err);
      toast.error('An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    signIn('google', { callbackUrl: '/dashboard' });
  };

  const handleForgotPassword = async () => {
    if (!email) {
      setError('Please enter your email to reset password.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await sendPasswordResetEmail(auth, email);
      toast.success('Password reset email sent! Check your inbox.');
    } catch (err: any) {
      setError(err.message);
      toast.error(err.message || 'Failed to send password reset email.');
      console.error('Forgot password error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 w-full max-w-md mx-auto">
      <Card className="bg-dc-white text-dc-black border-gray-200 shadow-lg rounded-xl">
        <CardHeader className="text-center p-6">
          <CardTitle className="text-3xl font-bold mb-2">
            Welcome Back!
          </CardTitle>
          <CardDescription className="text-dc-black">
            Sign in to access your AI Product Co-Pilot.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 pt-0">
          <div className="grid gap-6">
            {error && (
              <p className="text-red-500 text-sm text-center">{error}</p>
            )}
            <Button
              variant="outline"
              className="w-full flex items-center justify-center gap-2 bg-dc-white border border-gray-300 text-[#141414] py-3 hover:bg-gray-100 transition-colors rounded-lg"
              onClick={handleGoogleLogin}
              disabled={loading}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                width={20}
                height={20}>
                <path
                  d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
                  fill="currentColor"
                />
              </svg>
              Sign in with Google
            </Button>
          </div>

          <div className="after:border-dc-black/20 relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t my-4">
            <span className="bg-dc-white text-dc-black relative z-10 px-2">
              Or continue with
            </span>
          </div>

          <form onSubmit={handleEmailLogin} className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border-gray-300 focus-visible:ring-dc-black"
                disabled={loading}
              />
            </div>
            <div className="grid gap-3">
              <div className="flex items-center">
                <Label htmlFor="password">Password</Label>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="ml-auto text-sm underline-offset-4 hover:underline"
                  disabled={loading}>
                  Forgot your password?
                </button>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10 border-gray-300 focus-visible:ring-dc-black"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <Button
              type="submit"
              className="w-full bg-dc-black text-dc-white hover:bg-gray-800 py-3 rounded-lg"
              disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          <div className="text-center text-sm text-gray-500 mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/sign-up" className="underline underline-offset-4">
              Sign up
            </Link>
          </div>

          <div className="text-center text-xs text-balance text-gray-500 mt-4">
            By clicking continue, you agree to our{' '}
            <Link href="#" className="underline underline-offset-4">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="#" className="underline underline-offset-4">
              Privacy Policy
            </Link>
            .
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
