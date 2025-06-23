'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useAuthStore from '@/store/authStore';
import { UserRole } from '@/types/user';

interface RoleWrapperProps {
  children?: React.ReactNode;
  allowedRoles: UserRole[];
  fallbackRoute?: string;
}

const RoleWrapper: React.FC<RoleWrapperProps> = ({ 
  children, 
  allowedRoles, 
  fallbackRoute = '/dashboard' 
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    const checkRoleAccess = () => {
      setIsLoading(true);

      // If not authenticated, redirect to login
      if (!isAuthenticated || !user) {
        router.replace('/login');
        return;
      }

      // Check if user's role is in allowed roles
      if (allowedRoles.includes(user.role)) {
        setHasAccess(true);
      } else {
        // User doesn't have required role, redirect to fallback
        router.replace(fallbackRoute);
        return;
      }

      setIsLoading(false);
    };

    checkRoleAccess();
  }, [user, isAuthenticated, allowedRoles, fallbackRoute, router]);

  // Show loading spinner while checking role access
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-black border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-lg font-medium text-black">Checking permissions...</p>
        </div>
      </div>
    );
  }

  // If no access, don't render children (redirect is happening)
  if (!hasAccess) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="mb-4">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0H9m6-5v1a3 3 0 01-3 3H9a3 3 0 01-3-3v-1m12 0V9a3 3 0 00-3-3H6a3 3 0 00-3 3v3" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-black mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
          <p className="text-sm text-gray-500">Redirecting...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

const withRole = (allowedRoles: UserRole[], fallbackRoute?: string) => {
  return <P extends object>(WrappedComponent: React.ComponentType<P>) => {
    const RoleProtectedComponent: React.FC<P> = (props) => {
      return (
        <RoleWrapper allowedRoles={allowedRoles} fallbackRoute={fallbackRoute}>
          <WrappedComponent {...props} />
        </RoleWrapper>
      );
    };

    // Set display name for debugging
    RoleProtectedComponent.displayName = `withRole(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

    return RoleProtectedComponent;
  };
};

export default withRole; 