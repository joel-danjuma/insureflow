'use client';

import React from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import withRole from '@/hocs/withRole';
import useAuthStore from '@/store/authStore';
import { UserRole } from '@/types/user';

const ReportsPage = () => {
  const { user } = useAuthStore();

  return (
    <Layout title="Reports & Analytics">
      <div className="space-y-6">
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-bold text-white mb-4">Reports & Analytics</h2>
          <p className="text-gray-400 mb-4">
            View reports and analytics data. Accessible to Admin and Broker roles.
          </p>
          {/* Role-specific content */}
          {user?.role === UserRole.ADMIN && (
            <div className="mb-6 p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
              <h3 className="font-semibold text-blue-300 mb-2">Admin View</h3>
              <p className="text-sm text-blue-200">
                As an admin, you can see system-wide reports and all broker performance data.
              </p>
            </div>
          )}
          {user?.role === UserRole.BROKER && (
            <div className="mb-6 p-4 bg-green-900/20 border border-green-700 rounded-lg">
              <h3 className="font-semibold text-green-300 mb-2">Broker View</h3>
              <p className="text-sm text-green-200">
                As a broker, you can see your personal performance and commission reports.
              </p>
            </div>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-700 border border-gray-600 p-4 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Performance Reports</h3>
              <p className="text-sm text-gray-300">View performance metrics and KPIs</p>
            </div>
            <div className="bg-gray-700 border border-gray-600 p-4 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Financial Reports</h3>
              <p className="text-sm text-gray-300">Track revenue and commission data</p>
            </div>
            <div className="bg-gray-700 border border-gray-600 p-4 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Custom Reports</h3>
              <p className="text-sm text-gray-300">Generate custom analytics reports</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(withRole([UserRole.ADMIN, UserRole.BROKER])(ReportsPage)); 