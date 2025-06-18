'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm, { LoginFormData } from '@/components/LoginForm';
import { authService } from '@/services/api';
import useAuthStore from '@/store/authStore';

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const router = useRouter();
  const { setToken } = useAuthStore();

  const handleLogin = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(undefined);
    try {
      const response = await authService.login(data);
      setToken(response.access_token);
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
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-gray-900 mb-8">
          Sign in to your account
        </h2>
        <LoginForm onSubmit={handleLogin} isLoading={isLoading} error={error} />
      </div>
    </div>
  );
};

export default LoginPage; 