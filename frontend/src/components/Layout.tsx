import React from 'react';
import Sidebar from './Sidebar';
import { UserRole } from '@/types/user';

interface LayoutProps {
  children: React.ReactNode;
  userRole: UserRole;
}

const Layout: React.FC<LayoutProps> = ({ children, userRole }) => {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar userRole={userRole} />
      <main className="flex-1 flex flex-col">
        {/* You can add a header here if needed in the future */}
        <div className="flex-1 p-6 lg:p-8">
            {children}
        </div>
      </main>
    </div>
  );
};

export default Layout; 