'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import InsuranceFirmDashboard from '@/components/InsuranceFirmDashboard';
import BrokerDashboard from '@/components/BrokerDashboard';
import InsureFlowAdminDashboard from '@/components/InsureFlowAdminDashboard';
import useAuthStore from '@/store/authStore';
import { UserRole } from '@/types/user';

const DashboardPage = () => {
  const { user } = useAuthStore();
  const router = useRouter();

  // Redirect based on user role
  useEffect(() => {
    if (user) {
      // Keep all users on the same dashboard route but show different content
      // This maintains a single dashboard URL while providing role-specific views
    }
  }, [user, router]);

  if (!user) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin h-12 w-12 border-4 border-orange-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-lg font-medium text-white">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const getDashboardTitle = () => {
    switch (user.role) {
      case UserRole.ADMIN:
        return 'InsureFlow Admin Dashboard';
      case UserRole.BROKER:
        return 'Broker Dashboard';
      case UserRole.CUSTOMER:
        return 'Customer Dashboard';
      default:
        return 'Dashboard';
    }
  };

  return (
    <Layout userRole={user.role} title={getDashboardTitle()}>
      {/* Render appropriate dashboard based on user role */}
      {user.role === UserRole.ADMIN && <InsureFlowAdminDashboard />}
      {user.role === UserRole.INSURANCE_ADMIN && <InsuranceFirmDashboard />}
      {user.role === UserRole.BROKER && <BrokerDashboard />}
      {user.role === UserRole.CUSTOMER && (
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-white mb-4">Customer Dashboard</h2>
          <p className="text-gray-400">Customer dashboard coming soon...</p>
        </div>
      )}
    </Layout>
  );
};

// Apply auth protection
export default withAuth(DashboardPage); 