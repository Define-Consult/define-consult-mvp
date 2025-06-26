import { GalleryVerticalEnd } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';

import { LoginForm } from '@/components';

export default function LoginPage() {
  return (
    <div className="bg-dc-white flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <Link
          href="/"
          className="flex items-center gap-2 self-center font-medium">
          {/* Logo */}
          <Image
            src="/define-consult-logo.png"
            alt="Define Consult Logo"
            width={70}
            height={70}
            priority
            className="mb-3"
          />
          <span className="text-lg">define consult.®</span>
        </Link>
        <LoginForm />
      </div>
    </div>
  );
}
