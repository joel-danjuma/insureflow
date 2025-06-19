'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
// import withAuth from '@/hocs/withAuth'; // Auth is temporarily suspended for testing
import InsuranceFirmDashboard from '@/components/InsuranceFirmDashboard';
import BrokerDashboard from '@/components/BrokerDashboard';
import { UserRole } from '@/types/user';

const DashboardPage = () => {
  const [mockRole, setMockRole] = useState<UserRole>(UserRole.INSURANCE_FIRM);

  return (
    <Layout userRole={mockRole}>
      {/* --- MOCK ROLE SWITCHER FOR TESTING --- */}
      <div className="absolute top-4 right-4 bg-yellow-200 p-2 rounded shadow-lg text-sm z-50">
        <h4 className="font-bold mb-2">Testing Controls</h4>
        <p className="mb-2">Viewing as: <strong>{mockRole.replace('-', ' ').toUpperCase()}</strong></p>
        <div className="flex space-x-2">
          <button 
            onClick={() => setMockRole(UserRole.INSURANCE_FIRM)}
            className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
            disabled={mockRole === UserRole.INSURANCE_FIRM}
          >
            Insurance Firm
          </button>
          <button 
            onClick={() => setMockRole(UserRole.BROKER)}
            className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
            disabled={mockRole === UserRole.BROKER}
          >
            Broker
          </button>
        </div>
      </div>
      {/* --- END OF MOCK ROLE SWITCHER --- */}

      {mockRole === UserRole.INSURANCE_FIRM && <InsuranceFirmDashboard />}
      {mockRole === UserRole.BROKER && <BrokerDashboard />}
    </Layout>
  );
};

// export default withAuth(DashboardPage); // Auth is temporarily suspended
export default DashboardPage; 