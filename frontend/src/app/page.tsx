'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect directly to dashboard (authentication bypassed for debugging)
    router.replace('/dashboard');
  }, [router]);

  // Show loading while redirecting
  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin h-12 w-12 border-4 border-black border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-lg font-medium text-black">Loading...</p>
      </div>
    </div>
  );
}
