'use client';

import React from 'react';
import Link from 'next/link';
import { UserRole } from '@/types/user'; // We'll create this type file next

const commonLinks = [
  { href: '/dashboard', label: 'Dashboard', icon: 'House' },
  { href: '#', label: 'Policies', icon: 'File' },
];

const roleLinks = {
  [UserRole.INSURANCE_FIRM]: [
    { href: '#', label: 'Brokers', icon: 'Users' },
    { href: '#', label: 'Claims', icon: 'ShieldCheck' },
    { href: '#', label: 'Reports', icon: 'ChartBar' },
  ],
  [UserRole.BROKER]: [
    { href: '#', label: 'Clients', icon: 'Users' },
    { href: '#', label: 'Commissions', icon: 'CurrencyDollar' },
    { href: '#', label: 'Support', icon: 'Question' },
  ],
  [UserRole.CUSTOMER]: [],
};

const icons: { [key: string]: React.ReactNode } = {
    House: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0,1.14,1.14,0,0,0,.11.11l80,75.48A16,16,0,0,1,224,115.55Z"></path></svg>,
    Users: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M117.25,157.92a60,60,0,1,0-66.5,0A95.83,95.83,0,0,0,3.53,195.63a8,8,0,1,0,13.4,8.74,80,80,0,0,1,134.14,0,8,8,0,0,0,13.4-8.74A95.83,95.83,0,0,0,117.25,157.92ZM40,108a44,44,0,1,1,44,44A44.05,44.05,0,0,1,40,108Zm210.14,98.7a8,8,0,0,1-11.07-2.33A79.83,79.83,0,0,0,172,168a8,8,0,0,1,0-16,44,44,0,1,0-16.34-84.87,8,8,0,1,1-5.94-14.85,60,60,0,0,1,55.53,105.64,95.83,95.83,0,0,1,47.22,37.71A8,8,0,0,1,250.14,206.7Z"></path></svg>,
    File: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48V216Z"></path></svg>,
    CurrencyDollar: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M152,120H136V56h8a32,32,0,0,1,32,32,8,8,0,0,0,16,0,48.05,48.05,0,0,0-48-48h-8V24a8,8,0,0,0-16,0V40h-8a48,48,0,0,0,0,96h8v64H104a32,32,0,0,1-32-32,8,8,0,0,0-16,0,48.05,48.05,0,0,0,48,48h16v16a8,8,0,0,0,16,0V216h16a48,48,0,0,0,0-96Zm-40,0a32,32,0,0,1,0-64h8v64Zm40,80H136V136h16a32,32,0,0,1,0,64Z"></path></svg>,
    Question: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M140,180a12,12,0,1,1-12-12A12,12,0,0,1,140,180ZM128,72c-22.06,0-40,16.15-40,36v4a8,8,0,0,0,16,0v-4c0-11,10.77-20,24-20s24,9,24,20-10.77,20-24,20a8,8,0,0,0-8,8v8a8,8,0,0,0,16,0v-.72c18.24-3.35,32-17.9,32-35.28C168,88.15,150.06,72,128,72Zm104,56A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"></path></svg>,
    ShieldCheck: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M213,42.23a15.8,15.8,0,0,0-11.23-4.57c-29-3.2-61.5,0-83.77,0s-54.74-3.2-83.77,0A15.8,15.8,0,0,0,23,42.23V120c0,73.1,82.4,102.32,98.11,108.66a15.9,15.9,0,0,0,13.78,0C150.6,222.32,232,193.1,232,120V42.23ZM117.37,162.63l-32-32a8,8,0,0,1,11.32-11.32L112,135.31l58.63-58.62a8,8,0,0,1,11.32,11.32Z"></path></svg>,
    ChartBar: <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256"><path d="M240,208a8,8,0,0,1-8,8H32a8,8,0,0,1-8-8V48a8,8,0,0,1,16,0v32h64V48a8,8,0,0,1,16,0v56h64V48a8,8,0,0,1,16,0v80h32V48a8,8,0,0,1,16,0ZM112,96H48v96h64Zm80,40H128V48h64Z"></path></svg>,
};

interface SidebarProps {
  userRole: UserRole;
}

const Sidebar: React.FC<SidebarProps> = ({ userRole }) => {
  const links = [...commonLinks, ...(roleLinks[userRole] || [])];

  return (
    <aside className="flex flex-col w-64 bg-white p-4 border-r border-gray-200">
      <div className="flex flex-col mb-8">
        <h1 className="text-[#101418] text-base font-medium leading-normal">Acme Co</h1>
        <p className="text-[#5c738a] text-sm font-normal leading-normal">{userRole === UserRole.INSURANCE_FIRM ? 'Insurance Firm' : 'Broker Team'}</p>
      </div>
      <nav className="flex flex-col gap-2">
        {links.map(({ href, label, icon }) => (
          <Link
            key={label}
            href={href}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 aria-[current=page]:bg-gray-200 aria-[current=page]:text-gray-900"
            aria-current={label === 'Dashboard' ? 'page' : undefined}
          >
            <div className="text-[#101418]">{icons[icon]}</div>
            <p className="text-[#101418] text-sm font-medium leading-normal">{label}</p>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
