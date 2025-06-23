'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import LoginForm, { LoginFormData } from '@/components/LoginForm';
import { authService } from '@/services/api';
import useAuthStore from '@/store/authStore';
import withGuest from '@/hocs/withGuest';
import { UserRole } from '@/types/user';

const LoginClientContent = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const [successMessage, setSuccessMessage] = useState<string | undefined>(undefined);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAuth } = useAuthStore();

  useEffect(() => {
    if (searchParams.get('registered') === 'true') {
      setSuccessMessage('Registration successful! Please sign in with your new account.');
    }
  }, [searchParams]);

  const handleLogin = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(undefined);
    
    // For debugging: bypass API call and redirect directly to dashboard
    setTimeout(() => {
      // Set mock auth data
      setAuth('mock-token', {
        email: data.email,
        full_name: 'Admin User',
        role: UserRole.ADMIN,
        id: 1,
        username: 'admin',
        is_active: true,
        is_verified: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      
      router.push('/dashboard');
      setIsLoading(false);
    }, 1000);

    /* Original API call - commented out for debugging
    try {
      const response = await authService.login(data);
      
      // Set both token and user data in auth store
      setAuth(response.access_token, response.user);
      
      router.push('/dashboard');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
    */
  };

  return (
    <div className="w-full">
      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 border-2 border-green-200 rounded-none">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-green-700 font-medium">{successMessage}</p>
          </div>
        </div>
      )}
      
      <LoginForm onSubmit={handleLogin} isLoading={isLoading} error={error} />
      
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-600">
          Don&apos;t have an account?{' '}
          <a 
            href="/signup" 
            className="font-bold text-black hover:underline transition-all duration-200"
          >
            Create one here
          </a>
        </p>
      </div>
    </div>
  );
};

// Export the component wrapped with the HOC
export default function LoginClientPage() {
  const WrappedComponent = withGuest(LoginClientContent);
  return <WrappedComponent />;
} 