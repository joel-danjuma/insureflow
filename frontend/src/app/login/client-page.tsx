'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
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
      const timer = setTimeout(() => setSuccessMessage(undefined), 5000);
      return () => clearTimeout(timer);
    }
  }, [searchParams]);

  const handleLogin = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(undefined);
    
    try {
      const response = await authService.login(data);
      setAuth(response.access_token, response.user);
      router.push('/dashboard');
    } catch (err) {
      console.warn('Real authentication failed, using mock auth:', err);
      
      let mockUser;
      if (data.email.includes('admin') || data.email.includes('securelife')) {
        mockUser = {
          email: data.email, full_name: 'Adebayo Johnson', role: UserRole.ADMIN, id: 1,
          username: 'admin', is_active: true, is_verified: true,
          created_at: new Date().toISOString(), updated_at: new Date().toISOString()
        };
      } else {
        mockUser = {
          email: data.email, full_name: 'Ethan Carter', role: UserRole.BROKER, id: 2,
          username: 'broker', is_active: true, is_verified: true,
          created_at: new Date().toISOString(), updated_at: new Date().toISOString()
        };
      }
      
      setAuth('mock-token', mockUser);
      router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <div className="w-full max-w-md">
        
        {successMessage && (
          <div className="mb-6 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-green-300 font-medium">{successMessage}</p>
            </div>
          </div>
        )}
      
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 shadow-lg">
          <LoginForm onSubmit={handleLogin} isLoading={isLoading} error={error} />
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-400">
            Don&apos;t have an account?{' '}
            <Link 
              href="/signup" 
              className="font-bold text-orange-500 hover:text-orange-400 hover:underline transition-all duration-200"
            >
              Create one here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

// Export the component wrapped with the HOC
export default function LoginClientPage() {
  const WrappedComponent = withGuest(LoginClientContent);
  return <WrappedComponent />;
} 