import React, { Suspense } from 'react';
import LoginClientPage from './client-page';

const LoginPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex flex-col lg:flex-row text-white">
      {/* Left Panel - Branding */}
      <div className="w-full lg:w-1/2 bg-black flex items-center justify-center p-8 lg:p-12">
        <div className="max-w-md text-center">
          <h1 className="text-3xl lg:text-4xl font-bold mb-4">InsureFlow</h1>
          <p className="text-lg text-gray-300 mb-6 leading-relaxed">
            Streamline your insurance operations with our comprehensive broker management platform.
          </p>
          <div className="space-y-3 text-left text-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 border-2 border-orange-500 text-orange-500 flex-shrink-0 flex items-center justify-center rounded-full">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <span>Broker performance tracking</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 border-2 border-orange-500 text-orange-500 flex-shrink-0 flex items-center justify-center rounded-full">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <span>Squad Co payment integration</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 border-2 border-orange-500 text-orange-500 flex-shrink-0 flex items-center justify-center rounded-full">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <span>Real-time dashboard metrics</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-900">
        <div className="w-full max-w-md">
          <div className="text-center mb-6 lg:hidden">
            <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
          </div>
          <Suspense fallback={
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <div className="animate-pulse space-y-6">
                <div className="h-4 bg-gray-700 rounded w-1/4"></div>
                <div className="h-12 bg-gray-700 rounded"></div>
                <div className="h-4 bg-gray-700 rounded w-1/4"></div>
                <div className="h-12 bg-gray-700 rounded"></div>
                <div className="h-12 bg-orange-600 rounded"></div>
              </div>
            </div>
          }>
            <LoginClientPage />
          </Suspense>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 