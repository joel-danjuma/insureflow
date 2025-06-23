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
        <div className="bg-white border-2 border-black p-6">
          <h2 className="text-xl font-bold text-black mb-4">Admin Dashboard</h2>
          <p className="text-gray-600 mb-4">
            Welcome to the admin panel. This page is only accessible to users with Admin role.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-50 border border-gray-200 p-4">
              <h3 className="font-semibold text-black mb-2">User Management</h3>
              <p className="text-sm text-gray-600">Manage user accounts and permissions</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 p-4">
              <h3 className="font-semibold text-black mb-2">System Settings</h3>
              <p className="text-sm text-gray-600">Configure system-wide settings</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 p-4">
              <h3 className="font-semibold text-black mb-2">Analytics</h3>
              <p className="text-sm text-gray-600">View system analytics and reports</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(withRole([UserRole.ADMIN])(AdminPage)); 