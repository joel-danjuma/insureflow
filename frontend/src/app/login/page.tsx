import React, { Suspense } from 'react';
import LoginClientPage from './client-page';

const LoginPage = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-gray-900 mb-8">
          Sign in to your account
        </h2>
        <Suspense fallback={<div>Loading...</div>}>
          <LoginClientPage />
        </Suspense>
      </div>
    </div>
  );
};

export default LoginPage; 