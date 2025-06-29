'use client';

import { notFound } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { use } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import UserWhispererComponent from '@/components/dashboard/userWhisperer';
import MarketMavenComponent from '@/components/dashboard/marketMaven';
import NarrativeArchitectComponent from '@/components/dashboard/narrativeArchitect';

type AgentId = 'user-whisperer' | 'market-maven' | 'narrative-architect';

const agentComponents = {
  'user-whisperer': UserWhispererComponent,
  'market-maven': MarketMavenComponent,
  'narrative-architect': NarrativeArchitectComponent,
};

const agentNames = {
  'user-whisperer': 'User Whisperer',
  'market-maven': 'Market Maven',
  'narrative-architect': 'Narrative Architect',
};

interface AgentPageProps {
  params: Promise<{
    agent_id: string;
  }>;
}

export default function AgentPage({ params }: AgentPageProps) {
  const { data: session } = useSession();
  const { agent_id } = use(params);

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500">
            Please log in to access the agent workspace
          </p>
        </div>
      </div>
    );
  }

  // Validate agent_id
  if (!agentComponents[agent_id as AgentId]) {
    notFound();
  }

  const AgentComponent = agentComponents[agent_id as AgentId];
  const agentName = agentNames[agent_id as AgentId];

  return (
    <DashboardLayout>
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{agentName}</h1>
          <p className="text-gray-600 mt-1">
            AI-powered workspace for your {agentName.toLowerCase()} tasks
          </p>
        </div>

        {/* Agent Component */}
        <AgentComponent />
      </div>
    </DashboardLayout>
  );
}
