'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import CreateUserForm from '@/components/CreateUserForm';
import UserCreationSuccess from '@/components/UserCreationSuccess';
import useAuthStore from '@/store/authStore';
import { UserRole } from '@/types/user';

const SettingsPage = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('user-management');
  const [showCreateUserForm, setShowCreateUserForm] = useState(false);
  const [userCreationResult, setUserCreationResult] = useState<any>(null);

  // Handle user creation success
  const handleUserCreationSuccess = (result: any) => {
    setUserCreationResult(result);
    setShowCreateUserForm(false);
  };

  // Handle closing success modal
  const handleCloseSuccessModal = () => {
    setUserCreationResult(null);
  };

  // Only show user management for insurance admins
  const canManageUsers = user?.role === UserRole.INSURANCE_ADMIN || user?.role === UserRole.ADMIN;

  const tabs = [
    ...(canManageUsers ? [{ id: 'user-management', label: 'User Management', icon: '👥' }] : []),
    { id: 'general', label: 'General Settings', icon: '⚙️' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'security', label: 'Security', icon: '🔒' },
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-white text-3xl font-bold mb-2">Settings</h1>
            <p className="text-gray-400">Manage your account and application preferences</p>
          </div>

          {/* Tabs */}
          <div className="flex space-x-1 mb-8 bg-gray-800 p-1 rounded-lg">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
            {activeTab === 'user-management' && canManageUsers && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h2 className="text-white text-xl font-bold mb-2">User Management</h2>
                    <p className="text-gray-400">Create and manage broker users with virtual accounts</p>
                  </div>
                  <button
                    onClick={() => setShowCreateUserForm(!showCreateUserForm)}
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      showCreateUserForm
                        ? 'bg-gray-600 text-gray-300 hover:bg-gray-700'
                        : 'bg-orange-500 hover:bg-orange-600 text-white'
                    }`}
                  >
                    {showCreateUserForm ? 'Cancel' : 'Create New Broker User'}
                  </button>
                </div>

                {showCreateUserForm && (
                  <div className="mb-6">
                    <CreateUserForm
                      onSuccess={handleUserCreationSuccess}
                      onCancel={() => setShowCreateUserForm(false)}
                    />
                  </div>
                )}

                {!showCreateUserForm && (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg mb-4">👥</div>
                    <h3 className="text-white text-lg font-semibold mb-2">User Management</h3>
                    <p className="text-gray-400 mb-4">
                      Create new broker users with automatically generated passwords and virtual accounts.
                    </p>
                    <p className="text-gray-500 text-sm">
                      Click "Create New Broker User" to get started.
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'general' && (
              <div>
                <h2 className="text-white text-xl font-bold mb-6">General Settings</h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Company Name
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                      placeholder="Your company name"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Time Zone
                    </label>
                    <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500">
                      <option>Africa/Lagos (WAT)</option>
                      <option>UTC</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-white text-xl font-bold mb-6">Notification Settings</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-medium">Email Notifications</h3>
                      <p className="text-gray-400 text-sm">Receive notifications via email</p>
                    </div>
                    <input type="checkbox" className="toggle" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-medium">Payment Reminders</h3>
                      <p className="text-gray-400 text-sm">Get notified about overdue payments</p>
                    </div>
                    <input type="checkbox" className="toggle" defaultChecked />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-white text-xl font-bold mb-6">Security Settings</h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-white font-medium mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <input
                        type="password"
                        placeholder="Current password"
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                      />
                      <input
                        type="password"
                        placeholder="New password"
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                      />
                      <input
                        type="password"
                        placeholder="Confirm new password"
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                      />
                      <button className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors">
                        Update Password
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* User Creation Success Modal */}
        {userCreationResult && (
          <UserCreationSuccess
            result={userCreationResult}
            onClose={handleCloseSuccessModal}
          />
        )}
      </div>
    </Layout>
  );
};

export default SettingsPage;