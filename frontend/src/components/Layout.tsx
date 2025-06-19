import React from 'react';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="relative flex size-full min-h-screen flex-col bg-gray-50 group/design-root overflow-x-hidden">
      <Header />
      <main className="flex flex-1 justify-center py-5">
        <div className="layout-content-container flex flex-col w-full max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
        </div>
      </main>
    </div>
  );
};

export default Layout; 