'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
// import withAuth from '@/hocs/withAuth'; // Auth is temporarily suspended for testing
import AdminDashboard from '@/components/AdminDashboard';
import BrokerDashboard from '@/components/BrokerDashboard';

// This would ideally come from a shared schema definition
enum UserRole {
  ADMIN = 'admin',
  BROKER = 'broker',
  CUSTOMER = 'customer',
}

const DashboardPage = () => {
  const [mockRole, setMockRole] = useState<UserRole>(UserRole.ADMIN);

  return (
    <Layout>
      {/* --- MOCK ROLE SWITCHER FOR TESTING --- */}
      <div className="absolute top-4 right-4 bg-yellow-200 p-2 rounded shadow-lg text-sm">
        <h4 className="font-bold mb-2">Testing Controls</h4>
        <p className="mb-2">Viewing as: <strong>{mockRole.toUpperCase()}</strong></p>
        <div className="flex space-x-2">
          <button 
            onClick={() => setMockRole(UserRole.ADMIN)}
            className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
            disabled={mockRole === UserRole.ADMIN}
          >
            Admin View
          </button>
          <button 
            onClick={() => setMockRole(UserRole.BROKER)}
            className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
            disabled={mockRole === UserRole.BROKER}
          >
            Broker View
          </button>
        </div>
      </div>
      {/* --- END OF MOCK ROLE SWITCHER --- */}

      {mockRole === UserRole.ADMIN && <AdminDashboard />}
      {mockRole === UserRole.BROKER && <BrokerDashboard />}
    </Layout>
  );
};

// export default withAuth(DashboardPage); // Auth is temporarily suspended
export default DashboardPage; 