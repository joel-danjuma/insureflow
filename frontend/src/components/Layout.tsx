import React, { useState } from 'react';
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
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex min-h-screen bg-gray-900">
      {/* Fixed Sidebar */}
      {showSidebar && (
        <Sidebar 
          userRole={userRole} 
          isOpen={sidebarOpen} 
          onToggle={toggleSidebar}
        />
      )}
      
      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col ${showSidebar ? 'lg:ml-64' : ''}`}>
        {/* Fixed Header */}
        {showHeader && (
          <div className="fixed top-0 right-0 z-30 bg-gray-900" style={{ 
            left: showSidebar ? '16rem' : '0px', 
            width: showSidebar ? 'calc(100% - 16rem)' : '100%' 
          }}>
            <Header 
              title={title} 
              onToggleSidebar={showSidebar ? toggleSidebar : undefined}
              showSidebarToggle={showSidebar}
            />
          </div>
        )}
        
        {/* Scrollable Page Content */}
        <main className={`flex-1 p-4 lg:p-6 bg-gray-900 overflow-y-auto ${showHeader ? 'mt-[73px]' : ''} ${showSidebar ? 'lg:ml-0' : ''}`}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 