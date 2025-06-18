'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import SignUpForm, { SignUpFormData } from '@/components/SignUpForm';
import { authService } from '@/services/api';

const SignUpPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const router = useRouter();

  const handleSignUp = async (data: SignUpFormData) => {
    setIsLoading(true);
    setError(undefined);
    try {
      await authService.register(data);
      // On success, redirect to login with a success message/flag
      router.push('/login?registered=true');
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
          Create your account
        </h2>
        <SignUpForm onSubmit={handleSignUp} isLoading={isLoading} error={error} />
      </div>
    </div>
  );
};

export default SignUpPage; 