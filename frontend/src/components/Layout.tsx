import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { UserRole } from '@/types/user';

interface LayoutProps {
  children: React.ReactNode;
  userRole?: UserRole;
  title?: string;
  showSidebar?: boolean;
  showHeader?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  userRole, 
  title = 'Dashboard',
  showSidebar = true,
  showHeader = true 
}) => {
  return (
    <div className="flex min-h-screen bg-gray-900">
      {/* Sidebar */}
      {showSidebar && <Sidebar userRole={userRole} />}
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        {showHeader && <Header title={title} />}
        
        {/* Page Content */}
        <main className="flex-1 p-6 bg-gray-900">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 