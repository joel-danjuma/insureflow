'use client';

import React from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import withRole from '@/hocs/withRole';
import { UserRole } from '@/types/user';

const AdminPage = () => {
  return (
    <Layout title="Admin Panel">
      <div className="space-y-6">
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-bold text-white mb-4">Admin Dashboard</h2>
          <p className="text-gray-400 mb-4">
            Welcome to the admin panel. This page is only accessible to users with Admin role.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-700 border border-gray-600 p-4 rounded-lg">
              <h3 className="font-semibold text-white mb-2">User Management</h3>
              <p className="text-sm text-gray-300">Manage user accounts and permissions</p>
            </div>
            <div className="bg-gray-700 border border-gray-600 p-4 rounded-lg">
              <h3 className="font-semibold text-white mb-2">System Settings</h3>
              <p className="text-sm text-gray-300">Configure system-wide settings</p>
            </div>
            <div className="bg-gray-700 border border-gray-600 p-4 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Analytics</h3>
              <p className="text-sm text-gray-300">View system analytics and reports</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(withRole([UserRole.ADMIN])(AdminPage)); 