'use client';

import React from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import withRole from '@/hocs/withRole';
import { UserRole } from '@/types/user';

const BrokerPage = () => {
  return (
    <Layout title="Broker Portal">
      <div className="space-y-6">
        <div className="bg-white border-2 border-black p-6">
          <h2 className="text-xl font-bold text-black mb-4">Broker Portal</h2>
          <p className="text-gray-600 mb-4">
            Welcome to the broker portal. This page is only accessible to users with Broker role.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-50 border border-gray-200 p-4">
              <h3 className="font-semibold text-black mb-2">Client Management</h3>
              <p className="text-sm text-gray-600">Manage your client portfolio</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 p-4">
              <h3 className="font-semibold text-black mb-2">Commission Tracking</h3>
              <p className="text-sm text-gray-600">Track your commission earnings</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 p-4">
              <h3 className="font-semibold text-black mb-2">Payment Processing</h3>
              <p className="text-sm text-gray-600">Process bulk payments via Squad Co</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(withRole([UserRole.BROKER])(BrokerPage)); 