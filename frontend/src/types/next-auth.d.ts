import { DefaultSession, DefaultJWT } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      emailVerified?: boolean;
    } & DefaultSession['user'];
  }

  interface User {
    id: string;
    emailVerified?: boolean;
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    id: string;
    emailVerified?: boolean;
  }
}
