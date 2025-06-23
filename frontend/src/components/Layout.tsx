import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { UserRole } from '@/types/user';

interface LayoutProps {
  children: React.ReactNode;
  userRole: UserRole;
}

const Layout: React.FC<LayoutProps> = ({ children, userRole }) => {
  return (
    <div className="relative flex size-full min-h-screen flex-col bg-[#1a1a1a] group/design-root overflow-x-hidden">
      <Header />
      <div className="flex flex-1">
        <Sidebar userRole={userRole} />
        <main className="flex flex-1 flex-col px-6 py-5 bg-[#1a1a1a]">
            {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 