'use client';

import React from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import useQuery from '@/hooks/useQuery';
import { authService } from '@/services/api';
import useAuthStore from '@/store/authStore';
import AdminDashboard from '@/components/AdminDashboard';
import BrokerDashboard from '@/components/BrokerDashboard';

// This would ideally come from a shared schema definition
enum UserRole {
  ADMIN = 'admin',
  BROKER = 'broker',
  CUSTOMER = 'customer',
}

interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
}

const DashboardPage = () => {
  const { token } = useAuthStore();

  const fetchUser = React.useCallback(async () => {
    if (!token) throw new Error('No token found');
    return authService.getCurrentUser(token);
  }, [token]);

  const { data: user, isLoading, error } = useQuery<User>(fetchUser);

  if (isLoading) {
    return (
      <Layout>
        <div>Loading user information...</div>
      </Layout>
    );
  }

  if (error || !user) {
    return (
      <Layout>
        <div>Error loading user data. Please try logging in again.</div>
      </Layout>
    );
  }

  return (
    <Layout>
      {user.role === UserRole.ADMIN && <AdminDashboard />}
      {user.role === UserRole.BROKER && <BrokerDashboard />}
      {/* You could add a customer dashboard here as well */}
      {user.role === UserRole.CUSTOMER && <div>Customer Dashboard (Not Implemented)</div>}
    </Layout>
  );
};

export default withAuth(DashboardPage); 