import React from 'react';
import Sidebar from './Sidebar';
import { UserRole } from '@/types/user';

interface LayoutProps {
  children: React.ReactNode;
  userRole: UserRole;
}

const Layout: React.FC<LayoutProps> = ({ children, userRole }) => {
  return (
    <div className="flex h-screen bg-gray-100">
        <Sidebar userRole={userRole} />
        <main className="flex-1 p-8 overflow-y-auto">
            {children}
        </main>
    </div>
  );
};

export default Layout; 