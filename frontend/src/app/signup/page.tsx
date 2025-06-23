'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SignUpForm, { SignUpFormData } from '@/components/SignUpForm';
import { authService } from '@/services/api';
import withGuest from '@/hocs/withGuest';

const SignUpPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const router = useRouter();

  const handleSignUp = async (data: SignUpFormData) => {
    setIsLoading(true);
    setError(undefined);
    try {
      await authService.register(data);
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
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white">InsureFlow</h1>
          <p className="text-gray-400 mt-2">Create your account to get started.</p>
        </div>
      
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 shadow-lg">
          <SignUpForm onSubmit={handleSignUp} isLoading={isLoading} error={error} />
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-400">
            Already have an account?{' '}
            <Link 
              href="/login" 
              className="font-bold text-orange-500 hover:text-orange-400 hover:underline transition-all duration-200"
            >
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default withGuest(SignUpPage); 