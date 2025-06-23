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
      {/* Fixed Sidebar */}
      {showSidebar && <Sidebar userRole={userRole} />}
      
      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col ${showSidebar ? 'ml-64' : ''}`}>
        {/* Fixed Header */}
        {showHeader && (
          <div className="fixed top-0 right-0 z-30" style={{ left: showSidebar ? '256px' : '0px' }}>
            <Header title={title} />
          </div>
        )}
        
        {/* Scrollable Page Content */}
        <main className={`flex-1 p-6 bg-gray-900 overflow-y-auto ${showHeader ? 'mt-[73px]' : ''}`}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 