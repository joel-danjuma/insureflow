import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
        <main className="flex-1 p-8 overflow-y-auto">
            {children}
        </main>
    </div>
  );
};

export default Layout; 