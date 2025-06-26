'use client';

import Link from 'next/link';
import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/firebase/client';
import {
  createUserWithEmailAndPassword,
  sendEmailVerification,
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
import { Eye, EyeOff, Check, X } from 'lucide-react';
import { signIn } from 'next-auth/react';
import { toast } from 'sonner';

export default function SignupForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Password validation logic
  const passwordRequirements = useMemo(() => {
    const minLength = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(
      password
    );
    return {
      minLength,
      hasUppercase,
      hasLowercase,
      hasNumber,
      hasSpecialChar,
      isValid:
        minLength &&
        hasUppercase &&
        hasLowercase &&
        hasNumber &&
        hasSpecialChar,
    };
  }, [password]);

  const handleEmailSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!passwordRequirements.isValid) {
      setError('Please meet all password requirements.');
      setLoading(false);
      return;
    }

    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );
      if (userCredential.user) {
        await sendEmailVerification(userCredential.user);

        // Use toast instead of alert
        toast.success(
          'Verification email sent! Please check your inbox and verify your email to log in.'
        );

        // TODO: Call our backend API to create a user record in PostgreSQL
        // I'll build this endpoint in the next phase!
        // await fetch('/api/create-user', { method: 'POST', body: JSON.stringify({ uid: userCredential.user.uid, email: userCredential.user.email }) });

        router.push('/login');
      }
    } catch (err: any) {
      setError(err.message);
      console.error('Email signup error:', err);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const PasswordRequirementItem = ({
    text,
    isValid,
  }: {
    text: string;
    isValid: boolean;
  }) => (
    <div
      className={`flex items-center gap-3 p-2 rounded-lg transition-all duration-300 ${
        isValid
          ? 'bg-green-50 border border-green-200'
          : 'bg-gray-50 border border-gray-200'
      }`}>
      <div
        className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center transition-all duration-300 ${
          isValid ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-500'
        }`}>
        {isValid ? <Check size={12} /> : <X size={12} />}
      </div>
      <span
        className={`text-sm font-medium transition-colors duration-300 ${
          isValid ? 'text-green-700' : 'text-gray-600'
        }`}>
        {text}
      </span>
    </div>
  );

  return (
    <div className="flex flex-col gap-6 w-full max-w-md mx-auto">
      <Card className="bg-dc-white text-dc-black border-dc-gray-200 shadow-lg rounded-xl">
        <CardHeader className="text-center p-6">
          <CardTitle className="text-3xl font-bold mb-2">Get Started</CardTitle>
          <CardDescription className="text-dc-gray">
            Create your account to start automating product management tasks.
          </CardDescription>
        </CardHeader>

        <CardContent className="p-6 pt-0">
          <form onSubmit={handleEmailSignup} className="grid gap-4">
            {error && (
              <p className="text-red-500 text-sm text-center">{error}</p>
            )}

            <div className="grid gap-6">
              <Button
                variant="outline"
                className="w-full flex items-center justify-center gap-2 bg-dc-white border border-gray-300 text-dc-black py-3 hover:bg-gray-100 transition-colors rounded-lg"
                onClick={() => signIn('google', { callbackUrl: '/dashboard' })}
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
                Sign up with Google
              </Button>
            </div>

            <div className="after:border-dc-black/20 relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t">
              <span className="bg-dc-white text-dc-black relative z-10 px-2">
                Or sign up with
              </span>
            </div>

            <div className="grid gap-3">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border-dc-gray focus-visible:ring-dc-black"
                disabled={loading}
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10 border-dc-gray focus-visible:ring-dc-black"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-dc-gray hover:text-dc-black">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Inline password requirements */}
            {password && (
              <div className="text-sm text-gray-600">
                <span>Minimum </span>
                <span
                  className={
                    passwordRequirements.minLength
                      ? 'text-green-600'
                      : 'text-red-500'
                  }>
                  8 characters
                </span>
                <span>, at least </span>
                <span
                  className={
                    passwordRequirements.hasUppercase
                      ? 'text-green-600'
                      : 'text-red-500'
                  }>
                  1 uppercase
                </span>
                <span>, </span>
                <span
                  className={
                    passwordRequirements.hasLowercase
                      ? 'text-green-600'
                      : 'text-red-500'
                  }>
                  1 lowercase
                </span>
                <span>, and </span>
                <span
                  className={
                    passwordRequirements.hasNumber
                      ? 'text-green-600'
                      : 'text-red-500'
                  }>
                  1 number
                </span>
                {passwordRequirements.isValid && (
                  <Check size={16} className="inline ml-2 text-green-600" />
                )}
              </div>
            )}

            <Button
              type="submit"
              className="w-full bg-dc-black text-dc-white hover:bg-gray-800 py-3 rounded-lg"
              disabled={loading}>
              {loading ? 'Signing up...' : 'Sign Up'}
            </Button>
          </form>

          <div className="text-center text-sm text-dc-gray mt-6">
            Already have an account?{' '}
            <Link href="/login" className="underline underline-offset-4">
              Log in
            </Link>
          </div>

          <div className="text-center text-xs text-balance text-dc-gray mt-4">
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
