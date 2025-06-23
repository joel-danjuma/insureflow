'use client';

import React from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import InsuranceFirmDashboard from '@/components/InsuranceFirmDashboard';
import BrokerDashboard from '@/components/BrokerDashboard';
import useAuthStore from '@/store/authStore';
import { UserRole } from '@/types/user';

const mockUser = {
  email: 'admin@securelife.ng',
  full_name: 'Adebayo Johnson',
  role: UserRole.ADMIN,
};

const DashboardPage = () => {
  // const { user } = useAuthStore();
  const user = mockUser;

  if (!user) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin h-12 w-12 border-4 border-black border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-lg font-medium text-black">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout userRole={user.role} title="Dashboard">
      {/* Render appropriate dashboard based on user role */}
      {user.role === UserRole.ADMIN && <InsuranceFirmDashboard />}
      {user.role === UserRole.BROKER && <BrokerDashboard />}
      {user.role === UserRole.CUSTOMER && (
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-black mb-4">Customer Dashboard</h2>
          <p className="text-gray-600">Customer dashboard coming soon...</p>
        </div>
      )}
    </Layout>
  );
};

export default DashboardPage; 