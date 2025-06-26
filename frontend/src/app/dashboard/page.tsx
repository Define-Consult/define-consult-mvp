import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/next-auth/auth-options';
import { UserDashboard } from '@/components';

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);

  // Server-side redirect if not authenticated
  if (!session) {
    redirect('/login');
  }

  return <UserDashboard />;
}
