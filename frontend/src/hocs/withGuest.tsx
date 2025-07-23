'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useAuthStore from '@/store/authStore';

interface GuestWrapperProps {
  children?: React.ReactNode;
}

const GuestWrapper: React.FC<GuestWrapperProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { isAuthenticated, token, user } = useAuthStore();

  useEffect(() => {
    const checkAuthAndRedirect = async () => {
      setIsLoading(true);
      
      // If user is authenticated (has token and user data), redirect to dashboard
      if (isAuthenticated && token && user) {
        router.replace('/dashboard');
        return;
      }

      setIsLoading(false);
    };

    checkAuthAndRedirect();
  }, [isAuthenticated, token, user, router]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-black border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-lg font-medium text-black">Loading...</p>
        </div>
      </div>
    );
  }

  // If authenticated, don't render children (redirect is happening)
  if (isAuthenticated && token && user) {
    return null;
  }

  return <>{children}</>;
};

const withGuest = <P extends object>(WrappedComponent: React.ComponentType<P>) => {
  const GuestOnlyComponent: React.FC<P> = (props) => {
    return (
      <GuestWrapper>
        <WrappedComponent {...props} />
      </GuestWrapper>
    );
  };

  // Set display name for debugging
  GuestOnlyComponent.displayName = `withGuest(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return GuestOnlyComponent;
};

export default withGuest; 