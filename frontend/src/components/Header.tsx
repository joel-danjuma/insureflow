'use client';

import React, { useState } from 'react';
import useAuthStore from '@/store/authStore';
import { authService } from '@/services/api';
import { UserRole } from '@/types/user';

interface HeaderProps {
  title?: string;
  showUserMenu?: boolean;
}

const Header: React.FC<HeaderProps> = ({ title = 'Dashboard', showUserMenu = true }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const { user, logout } = useAuthStore();

  const getRoleDisplayName = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'Admin';
      case UserRole.BROKER:
        return 'Broker';
      case UserRole.CUSTOMER:
        return 'Customer';
      default:
        return 'User';
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      logout();
      setShowDropdown(false);
    } catch (error) {
      console.error('Logout failed:', error);
      // Force logout on error
      logout();
      setShowDropdown(false);
    }
  };

  return (
    <header className="bg-white border-b-2 border-black px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Title */}
        <div>
          <h1 className="text-2xl font-bold text-black">{title}</h1>
        </div>

        {/* Right Side - User Menu & Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 text-black hover:bg-gray-100 border-2 border-transparent hover:border-black transition-all duration-200">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 256 256">
              <path d="M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,216ZM48,184c7.7-13.24,16-43.92,16-80a64,64,0,1,1,128,0c0,36.05,8.28,66.73,16,80Z"/>
            </svg>
          </button>

          {/* User Profile Menu */}
          {showUserMenu && user && (
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="flex items-center space-x-3 p-2 border-2 border-transparent hover:border-black transition-all duration-200"
              >
                {/* Avatar */}
                <div className="w-8 h-8 bg-black text-white flex items-center justify-center text-sm font-bold">
                  {getInitials(user.full_name)}
                </div>
                
                {/* User Info */}
                <div className="text-left hidden md:block">
                  <p className="text-sm font-medium text-black">{user.full_name}</p>
                  <p className="text-xs text-gray-600">{getRoleDisplayName(user.role)}</p>
                </div>

                {/* Dropdown Arrow */}
                <svg
                  className={`w-4 h-4 text-black transition-transform duration-200 ${
                    showDropdown ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {showDropdown && (
                <>
                  {/* Backdrop */}
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowDropdown(false)}
                  />
                  
                  {/* Menu */}
                  <div className="absolute right-0 mt-2 w-64 bg-white border-2 border-black shadow-lg z-20">
                    {/* User Info */}
                    <div className="p-4 border-b-2 border-black">
                      <p className="font-medium text-black">{user.full_name}</p>
                      <p className="text-sm text-gray-600">{user.email}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {getRoleDisplayName(user.role)} • {user.is_verified ? 'Verified' : 'Unverified'}
                      </p>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                      <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-50 flex items-center space-x-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                          <path d="M230.92,212c-15.23-26.33-38.7-45.21-66.09-54.16a72,72,0,1,0-73.66,0C63.78,166.78,40.31,185.66,25.08,212a8,8,0,1,0,13.85,8c18.84-32.56,52.14-52,89.07-52s70.23,19.44,89.07,52a8,8,0,1,0,13.85-8ZM72,96a56,56,0,1,1,56,56A56.06,56.06,0,0,1,72,96Z"/>
                        </svg>
                        <span>Profile</span>
                      </button>
                      
                      <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-50 flex items-center space-x-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                          <path d="M128,80a48,48,0,1,0,48,48A48.05,48.05,0,0,0,128,80Zm0,80a32,32,0,1,1,32-32A32,32,0,0,1,128,160Zm88-29.84q.06-2.16,0-4.32l14.92-18.64a8,8,0,0,0,1.48-7.06,107.6,107.6,0,0,0-10.88-26.25,8,8,0,0,0-6-3.93l-23.72-2.64q-1.48-1.56-3.06-3.05L221.38,40.5a8,8,0,0,0-3.93-6,107.89,107.89,0,0,0-26.25-10.87,8,8,0,0,0-7.06,1.49L165.5,40.05q-2.16-.06-4.32,0L142.54,25.13a8,8,0,0,0-7.06-1.48A107.6,107.6,0,0,0,109.23,34.5a8,8,0,0,0-3.93,6L102.66,64.27q-1.56,1.49-3.05,3.06L75.88,64.69a8,8,0,0,0-6,3.93,107.89,107.89,0,0,0-10.87,26.25,8,8,0,0,0,1.49,7.06L75.41,120.5q-.06,2.16,0,4.32L60.49,143.46a8,8,0,0,0-1.48,7.06,107.6,107.6,0,0,0,10.88,26.25,8,8,0,0,0,6,3.93l23.72,2.64q1.49,1.56,3.06,3.05L34.62,215.5a8,8,0,0,0,3.93,6,107.89,107.89,0,0,0,26.25,10.87,8,8,0,0,0,7.06-1.49L90.5,215.95q2.16.06,4.32,0l18.64,14.92a8,8,0,0,0,7.06,1.48,107.6,107.6,0,0,0,26.25-10.88,8,8,0,0,0,3.93-6l2.64-23.72q1.56-1.48,3.05-3.06l23.72,2.64a8,8,0,0,0,6-3.93,107.89,107.89,0,0,0,10.87-26.25,8,8,0,0,0-1.49-7.06Zm-16.1-6.5a73.93,73.93,0,0,1,0,8.68,8,8,0,0,0,1.74,5.48l14.19,17.73a91.57,91.57,0,0,1-6.23,15L187,173.11a8,8,0,0,0-5.1,2.64,74.11,74.11,0,0,1-6.14,6.14,8,8,0,0,0-2.64,5.1l-2.51,22.58a91.32,91.32,0,0,1-15,6.23l-17.74-14.19a8,8,0,0,0-5.48-1.74,73.93,73.93,0,0,1-8.68,0,8,8,0,0,0-5.48,1.74L109.94,215.8a91.57,91.57,0,0,1-15-6.23L82.89,187a8,8,0,0,0-2.64-5.1,74.11,74.11,0,0,1-6.14-6.14,8,8,0,0,0-5.1-2.64L46.43,170.6a91.32,91.32,0,0,1-6.23-15l14.19-17.74a8,8,0,0,0,1.74-5.48,73.93,73.93,0,0,1,0-8.68,8,8,0,0,0-1.74-5.48L40.2,100.49a91.57,91.57,0,0,1,6.23-15L69,87.89a8,8,0,0,0,5.1-2.64,74.11,74.11,0,0,1,6.14-6.14,8,8,0,0,0,2.64-5.1L85.4,51.43a91.32,91.32,0,0,1,15-6.23L118.2,59.39a8,8,0,0,0,5.48,1.74,73.93,73.93,0,0,1,8.68,0,8,8,0,0,0,5.48-1.74L155.58,45.2a91.57,91.57,0,0,1,15,6.23L173.11,74a8,8,0,0,0,2.64,5.1,74.11,74.11,0,0,1,6.14,6.14,8,8,0,0,0,5.1,2.64l22.58,2.51a91.32,91.32,0,0,1,6.23,15l-14.19,17.74A8,8,0,0,0,199.87,123.66Z"/>
                        </svg>
                        <span>Settings</span>
                      </button>

                      <hr className="my-2 border-gray-200" />

                      <button
                        onClick={handleLogout}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                          <path d="M120,216a8,8,0,0,1-8,8H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32h64a8,8,0,0,1,0,16H48V208h64A8,8,0,0,1,120,216Zm109.66-93.66-40-40a8,8,0,0,0-11.32,11.32L204.69,120H112a8,8,0,0,0,0,16h92.69l-26.35,26.34a8,8,0,0,0,11.32,11.32l40-40A8,8,0,0,0,229.66,122.34Z"/>
                        </svg>
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 