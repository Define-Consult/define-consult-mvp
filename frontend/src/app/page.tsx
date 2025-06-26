'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState('Checking...');

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/status');
        if (response.ok) {
          const data = await response.json();
          setBackendStatus(data.status);
        } else {
          setBackendStatus('Offline');
        }
      } catch (error) {
        setBackendStatus('Offline');
      }
    };
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main
      className="flex flex-col items-center justify-center 
    min-h-screen p-8 md:p-24 bg-[#F5F5F5] text-[#141414]
    font-sans">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center text-center max-w-4xl w-full">
        {/* Logo */}
        <Image
          src="/define-consult-logo.png"
          alt="Define Consult Logo"
          width={80}
          height={80}
          priority
          className="mb-6 md:mb-8"
        />

        {/* Main Headline */}
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tighter leading-tight mb-4">
          Define Consult: Your AI Product Co-Pilot
        </h1>

        {/* Subheading */}
        <p className="text-base md:text-xl text-gray-700 max-w-2xl mb-8 md:mb-12">
          Autonomous AI agents that transform raw data into actionable product
          strategies and compelling evangelism, freeing you to focus on
          innovation, not busywork.
        </p>

        <Button
          className="bg-[#141414] text-white font-bold py-4 px-10 
        rounded-lg shadow-lg hover:bg-gray-800 transition-colors text-lg
        md:text-xl h-auto">
          Get Started Free
        </Button>
      </div>

      {/* Backend Status Indicator */}
      <div className="absolute bottom-8 text-center w-full">
        <p className="text-sm text-gray-500">
          Backend API Status:{' '}
          <span
            className={
              backendStatus === 'ok'
                ? 'text-green-600 font-bold'
                : 'text-red-600 font-bold'
            }>
            {backendStatus.toUpperCase()}
          </span>
        </p>
      </div>
    </main>
  );
}
