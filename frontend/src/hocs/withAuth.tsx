'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useAuthStore from '@/store/authStore';
import { authService } from '@/services/api';

interface AuthWrapperProps {
  children?: React.ReactNode;
}

const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isValidating, setIsValidating] = useState(false);
  const router = useRouter();
  const { token, user, setAuth, logout, isAuthenticated } = useAuthStore();

  useEffect(() => {
    const validateAndInitAuth = async () => {
      setIsLoading(true);
      
      // If no token, redirect to login
      if (!token) {
        setIsLoading(false);
        router.replace('/login');
        return;
      }

      // If we have token but no user data, fetch user data
      if (token && !user) {
        setIsValidating(true);
        try {
          const userData = await authService.getCurrentUser(token);
          setAuth(token, userData);
        } catch (error) {
          console.error('Failed to validate token:', error);
          logout();
          router.replace('/login');
          return;
        } finally {
          setIsValidating(false);
        }
      }

      setIsLoading(false);
    };

    validateAndInitAuth();
  }, [token, user, setAuth, logout, router]);

  // Show loading spinner while checking authentication
  if (isLoading || isValidating) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-black border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-lg font-medium text-black">
            {isValidating ? 'Validating session...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  // If not authenticated after validation, don't render children
  if (!isAuthenticated || !token || !user) {
    return null;
  }

  return <>{children}</>;
};

const withAuth = <P extends object>(WrappedComponent: React.ComponentType<P>) => {
  const AuthenticatedComponent: React.FC<P> = (props) => {
    return (
      <AuthWrapper>
        <WrappedComponent {...props} />
      </AuthWrapper>
    );
  };

  // Set display name for debugging
  AuthenticatedComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return AuthenticatedComponent;
};

export default withAuth; 