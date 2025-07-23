'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { UserRole } from '@/types/user';
import useAuthStore from '@/store/authStore';
import { useBrokerProfile } from '@/hooks/useQuery';

const commonLinks = [
  { href: '/dashboard', label: 'Dashboard', icon: 'House' },
  // { href: '/policies', label: 'Policies', icon: 'File' }, // Commented out - not working
];

const roleLinks = {
  [UserRole.ADMIN]: [
    // { href: '/brokers', label: 'Brokers', icon: 'Users' }, // Commented out - not working
    // { href: '/claims', label: 'Claims', icon: 'ShieldCheck' }, // Commented out - not working
    { href: '/policies/create', label: 'Create Policy', icon: 'File' },
    { href: '/reports', label: 'Reports', icon: 'ChartBar' },
    // { href: '/settings', label: 'Settings', icon: 'Gear' }, // Commented out - not working
    { href: '/reminders', label: 'Send Reminders', icon: 'Bell' },
  ],
  [UserRole.BROKER]: [
    { href: '/policies/create', label: 'Create Policy', icon: 'File' },
    { href: '/clients', label: 'Clients', icon: 'Users' },
    { href: '/payments', label: 'Payments', icon: 'CurrencyDollar' },
    { href: '/commissions', label: 'Commissions', icon: 'Wallet' },
    { href: '/support', label: 'Support', icon: 'Question' },
  ],
  [UserRole.CUSTOMER]: [
    { href: '/my-policies', label: 'My Policies', icon: 'File' },
    { href: '/payments', label: 'Payments', icon: 'CurrencyDollar' },
    { href: '/support', label: 'Support', icon: 'Question' },
  ],
};

const icons: { [key: string]: React.ReactNode } = {
  House: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0,1.14,1.14,0,0,0,.11.11l80,75.48A16,16,0,0,1,224,115.55Z"/>
    </svg>
  ),
  Users: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M117.25,157.92a60,60,0,1,0-66.5,0A95.83,95.83,0,0,0,3.53,195.63a8,8,0,1,0,13.4,8.74,80,80,0,0,1,134.14,0,8,8,0,0,0,13.4-8.74A95.83,95.83,0,0,0,117.25,157.92ZM40,108a44,44,0,1,1,44,44A44.05,44.05,0,0,1,40,108Zm210.14,98.7a8,8,0,0,1-11.07-2.33A79.83,79.83,0,0,0,172,168a8,8,0,0,1,0-16,44,44,0,1,0-16.34-84.87,8,8,0,1,1-5.94-14.85,60,60,0,0,1,55.53,105.64,95.83,95.83,0,0,1,47.22,37.71A8,8,0,0,1,250.14,206.7Z"/>
    </svg>
  ),
  File: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48V216Z"/>
    </svg>
  ),
  CurrencyDollar: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M152,120H136V56h8a32,32,0,0,1,32,32,8,8,0,0,0,16,0,48.05,48.05,0,0,0-48-48h-8V24a8,8,0,0,0-16,0V40h-8a48,48,0,0,0,0,96h8v64H104a32,32,0,0,1-32-32,8,8,0,0,0-16,0,48.05,48.05,0,0,0,48,48h16v16a8,8,0,0,0,16,0V216h16a48,48,0,0,0,0-96Zm-40,0a32,32,0,0,1,0-64h8v64Zm40,80H136V136h16a32,32,0,0,1,0,64Z"/>
    </svg>
  ),
  Wallet: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M216,64H56a8,8,0,0,1,0-16H192a8,8,0,0,0,0-16H56A24,24,0,0,0,32,56V184a24,24,0,0,0,24,24H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64Zm-36,80a12,12,0,1,1,12-12A12,12,0,0,1,180,144Z"/>
    </svg>
  ),
  Question: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M140,180a12,12,0,1,1-12-12A12,12,0,0,1,140,180ZM128,72c-22.06,0-40,16.15-40,36v4a8,8,0,0,0,16,0v-4c0-11,10.77-20,24-20s24,9,24,20-10.77,20-24,20a8,8,0,0,0-8,8v8a8,8,0,0,0,16,0v-.72c18.24-3.35,32-17.9,32-35.28C168,88.15,150.06,72,128,72Zm104,56A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"/>
    </svg>
  ),
  ShieldCheck: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M208,40H48A16,16,0,0,0,32,56V200a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V56A16,16,0,0,0,208,40ZM172.24,99.76l-48,48a8,8,0,0,1-11.31,0l-24-24a8,8,0,0,1,11.31-11.31L118.69,130.9l42.35-42.35a8,8,0,0,1,11.31,11.31Z"/>
    </svg>
  ),
  ChartBar: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M224,200h-8V40a8,8,0,0,0-16,0V200H184V88a8,8,0,0,0-16,0V200H152V120a8,8,0,0,0-16,0v80H120V160a8,8,0,0,0-16,0v40H88V72a8,8,0,0,0-16,0V200H64V104a8,8,0,0,0-16,0v96H32a8,8,0,0,0,0,16H224a8,8,0,0,0,0-16Z"/>
    </svg>
  ),
  Gear: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M128,80a48,48,0,1,0,48,48A48.05,48.05,0,0,0,128,80Zm0,80a32,32,0,1,1,32-32A32,32,0,0,1,128,160Zm88-29.84q.06-2.16,0-4.32l14.92-18.64a8,8,0,0,0,1.48-7.06,107.6,107.6,0,0,0-10.88-26.25,8,8,0,0,0-6-3.93l-23.72-2.64q-1.48-1.56-3.06-3.05L221.38,40.5a8,8,0,0,0-3.93-6,107.89,107.89,0,0,0-26.25-10.87,8,8,0,0,0-7.06,1.49L165.5,40.05q-2.16-.06-4.32,0L142.54,25.13a8,8,0,0,0-7.06-1.48A107.6,107.6,0,0,0,109.23,34.5a8,8,0,0,0-3.93,6L102.66,64.27q-1.56,1.49-3.05,3.06L75.88,64.69a8,8,0,0,0-6,3.93,107.89,107.89,0,0,0-10.87,26.25,8,8,0,0,0,1.49,7.06L75.41,120.5q-.06,2.16,0,4.32L60.49,143.46a8,8,0,0,0-1.48,7.06,107.6,107.6,0,0,0,10.88,26.25,8,8,0,0,0,6,3.93l23.72,2.64q1.49,1.56,3.06,3.05L34.62,215.5a8,8,0,0,0,3.93,6,107.89,107.89,0,0,0,26.25,10.87,8,8,0,0,0,7.06-1.49L90.5,215.95q2.16.06,4.32,0l18.64,14.92a8,8,0,0,0,7.06,1.48,107.6,107.6,0,0,0,26.25-10.88,8,8,0,0,0,3.93-6l2.64-23.72q1.56-1.48,3.05-3.06l23.72,2.64a8,8,0,0,0,6-3.93,107.89,107.89,0,0,0,10.87-26.25,8,8,0,0,0-1.49-7.06Zm-16.1-6.5a73.93,73.93,0,0,1,0,8.68,8,8,0,0,0,1.74,5.48l14.19,17.73a91.57,91.57,0,0,1-6.23,15L187,173.11a8,8,0,0,0-5.1,2.64,74.11,74.11,0,0,1-6.14,6.14,8,8,0,0,0-2.64,5.1l-2.51,22.58a91.32,91.32,0,0,1-15,6.23l-17.74-14.19a8,8,0,0,0-5.48-1.74,73.93,73.93,0,0,1-8.68,0,8,8,0,0,0-5.48,1.74L109.94,215.8a91.57,91.57,0,0,1-15-6.23L82.89,187a8,8,0,0,0-2.64-5.1,74.11,74.11,0,0,1-6.14-6.14,8,8,0,0,0-5.1-2.64L46.43,170.6a91.32,91.32,0,0,1-6.23-15l14.19-17.74a8,8,0,0,0,1.74-5.48,73.93,73.93,0,0,1,0-8.68,8,8,0,0,0-1.74-5.48L40.2,100.49a91.57,91.57,0,0,1,6.23-15L69,87.89a8,8,0,0,0,5.1-2.64,74.11,74.11,0,0,1,6.14-6.14,8,8,0,0,0,2.64-5.1L85.4,51.43a91.32,91.32,0,0,1,15-6.23L118.2,59.39a8,8,0,0,0,5.48,1.74,73.93,73.93,0,0,1,8.68,0,8,8,0,0,0,5.48-1.74L155.58,45.2a91.57,91.57,0,0,1,15,6.23L173.11,74a8,8,0,0,0,2.64,5.1,74.11,74.11,0,0,1,6.14,6.14,8,8,0,0,0,5.1,2.64l22.58,2.51a91.32,91.32,0,0,1,6.23,15l-14.19,17.74A8,8,0,0,0,199.87,123.66Z"/>
    </svg>
  ),
  Bell: (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
      <path d="M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,216ZM48,184c7.7-13.24,16-43.92,16-80a64,64,0,1,1,128,0c0,36.05,8.28,66.73,16,80Z"/>
    </svg>
  ),
};

interface SidebarProps {
  userRole?: UserRole;
  isOpen?: boolean;
  onToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ userRole, isOpen = true, onToggle }) => {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const [isMobile, setIsMobile] = useState(false);
  
  // Use userRole prop or fall back to user from store
  const currentRole = userRole || user?.role || UserRole.BROKER;
  const links = [...commonLinks, ...(roleLinks[currentRole] || [])];

  // Get broker profile data only if user is a broker
  const { data: brokerProfile } = useBrokerProfile();

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Get company name based on user role and data
  const getCompanyName = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'Sovereign Trust';
      case UserRole.BROKER:
        // Use broker's name (like "SCIB") first, then agency name if available
        if (brokerProfile?.name) {
          return brokerProfile.name;
        } else if (brokerProfile?.agency_name) {
          return brokerProfile.agency_name;
        }
        return 'Broker';
      case UserRole.CUSTOMER:
        return 'Customer Portal';
      default:
        return 'InsureFlow';
    }
  };

  const getRoleDisplayName = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'Administrator';
      case UserRole.BROKER:
        return 'Insurance Broker';
      case UserRole.CUSTOMER:
        return 'Customer';
      default:
        return 'User';
    }
  };

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/' || pathname === '/dashboard';
    }
    return pathname === href;
  };

  const handleLinkClick = () => {
    if (isMobile && onToggle) {
      onToggle();
    }
  };

  const companyName = getCompanyName(currentRole);
  // Better truncation for sidebar space
  const companyDisplayName = companyName.length > 16 ? companyName.substring(0, 16) + '...' : companyName;

  if (isMobile) {
    return (
      <>
        {/* Mobile Overlay */}
        {isOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
            onClick={onToggle}
          />
        )}
        
        {/* Mobile Sidebar */}
        <aside className={`fixed left-0 top-0 z-40 flex flex-col w-64 bg-gray-900 border-r border-gray-700 h-screen transform transition-transform duration-300 ease-in-out lg:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}>
          {/* Header */}
          <div className="p-6 border-b border-gray-700 h-[73px] flex flex-col justify-center">
            <h1 className="text-xl font-bold text-white mb-1 leading-tight" title={companyName}>
              {companyDisplayName}
            </h1>
            <p className="text-sm text-gray-400">
              {getRoleDisplayName(currentRole)}
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-1">
              {links.map(({ href, label, icon }) => {
                const active = isActive(href);
                return (
                  <Link
                    key={label}
                    href={href}
                    onClick={handleLinkClick}
                    className={`flex items-center space-x-3 px-4 py-3 text-sm font-medium transition-all duration-200 rounded-lg ${
                      active
                        ? 'bg-orange-500 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <div className={`${active ? 'text-white' : 'text-gray-400'}`}>
                      {icons[icon]}
                    </div>
                    <span>{label}</span>
                  </Link>
                );
              })}
            </div>
          </nav>
        </aside>
      </>
    );
  }

  // Desktop Sidebar
  return (
    <aside className="fixed left-0 top-0 z-40 flex flex-col w-64 bg-gray-900 border-r border-gray-700 h-screen lg:block hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-700 h-[73px] flex flex-col justify-center">
        <h1 className="text-xl font-bold text-white mb-1 leading-tight" title={companyName}>
          {companyDisplayName}
        </h1>
        <p className="text-sm text-gray-400">
          {getRoleDisplayName(currentRole)}
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto">
        <div className="space-y-1">
          {links.map(({ href, label, icon }) => {
            const active = isActive(href);
            return (
              <Link
                key={label}
                href={href}
                className={`flex items-center space-x-3 px-4 py-3 text-sm font-medium transition-all duration-200 rounded-lg ${
                  active
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <div className={`${active ? 'text-white' : 'text-gray-400'}`}>
                  {icons[icon]}
                </div>
                <span>{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;
