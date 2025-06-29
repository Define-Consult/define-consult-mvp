import type { NextAuthOptions } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import CredentialsProvider from 'next-auth/providers/credentials';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase/client';

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // Use Firebase client SDK to sign in
          const userCredential = await signInWithEmailAndPassword(
            auth,
            credentials.email,
            credentials.password
          );
          const user = userCredential.user;

          if (user) {
            return {
              id: user.uid,
              name: user.displayName || user.email?.split('@')[0] || 'User',
              email: user.email,
              image: user.photoURL,
              emailVerified: Boolean(user.emailVerified),
            };
          }
          return null;
        } catch (error: any) {
          console.error('Firebase login error:', error);

          return null;
        }
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/login',
    error: '/login',
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
        token.emailVerified = Boolean(user.emailVerified);
      }

      // For Google OAuth, create user in Firebase and sync with backend
      if (
        account?.provider === 'google' &&
        user &&
        account?.providerAccountId
      ) {
        try {
          // First, create or get the user in Firebase via our backend
          const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

          // Create Firebase user via backend (which has admin SDK)
          const firebaseResponse = await fetch(
            `${backendUrl}/api/v1/auth/create-or-get-firebase-user`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                email: user.email,
                name: user.name,
                avatar_url: user.image,
                provider: 'google',
                provider_id: account.providerAccountId,
              }),
            }
          );

          if (firebaseResponse.ok) {
            const firebaseUser = await firebaseResponse.json();
            token.id = firebaseUser.firebase_uid;
            console.log(
              'Successfully created/got Firebase user:',
              firebaseUser.firebase_uid
            );

            // Now sync with our PostgreSQL backend
            const syncResponse = await fetch(
              `${backendUrl}/api/v1/users/sync`,
              {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  firebase_uid: firebaseUser.firebase_uid,
                  email: user.email,
                  name: user.name,
                  avatar_url: user.image,
                }),
              }
            );

            if (syncResponse.ok) {
              console.log('Successfully synced Google user with backend');
            } else {
              console.error(
                'Failed to sync Google user with backend:',
                await syncResponse.text()
              );
            }
          } else {
            console.error(
              'Failed to create Firebase user:',
              await firebaseResponse.text()
            );
            // Fallback to using Google ID
            token.id = account.providerAccountId;
          }
        } catch (error) {
          console.error(
            'Error creating Firebase user or syncing with backend:',
            error
          );
          // Fallback to using Google ID
          token.id = account.providerAccountId;
        }
      }

      return token;
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as string;
        session.user.emailVerified = Boolean(token.emailVerified);
      }
      return session;
    },
    async redirect({ url, baseUrl }) {
      // Always redirect to dashboard after successful authentication
      if (url.startsWith('/') || url.startsWith(baseUrl)) {
        return `${baseUrl}/dashboard`;
      }
      return `${baseUrl}/dashboard`;
    },
  },
  debug: process.env.NODE_ENV === 'development',
};
