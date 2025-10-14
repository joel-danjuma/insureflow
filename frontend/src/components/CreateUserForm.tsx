'use client';

import React, { useState } from 'react';
import { userService } from '@/services/api';

interface CreateUserFormProps {
  onSuccess?: (result: any) => void;
  onCancel?: () => void;
}

interface FormData {
  email: string;
  full_name: string;
  username: string;
  phone_number: string;
  organization_name: string;
  bvn: string;
  date_of_birth: string;
  gender: string;
  address: string;
}

const CreateUserForm: React.FC<CreateUserFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    full_name: '',
    username: '',
    phone_number: '',
    organization_name: '',
    bvn: '',
    date_of_birth: '',
    gender: '',
    address: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Filter out empty optional fields
      const cleanedData = Object.entries(formData).reduce((acc, [key, value]) => {
        if (value.trim() !== '') {
          acc[key] = value.trim();
        }
        return acc;
      }, {} as any);

      // Ensure required fields are present
      if (!cleanedData.email || !cleanedData.full_name || !cleanedData.username) {
        setError('Email, Full Name, and Username are required fields.');
        return;
      }

      const result = await userService.createBrokerUser(cleanedData);
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err: any) {
      console.error('Error creating broker user:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to create user. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-white text-xl font-bold">Create New Broker User</h3>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-6">
          <div className="text-red-400 text-sm">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Required Fields */}
          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Email Address <span className="text-red-400">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="john.doe@example.com"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Full Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Username <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="johndoe"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="+234 801 234 5678"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Organization Name
            </label>
            <input
              type="text"
              name="organization_name"
              value={formData.organization_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="ABC Insurance Brokers"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              BVN (Bank Verification Number)
            </label>
            <input
              type="text"
              name="bvn"
              value={formData.bvn}
              onChange={handleInputChange}
              maxLength={11}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="12345678901"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Date of Birth
            </label>
            <input
              type="date"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Gender
            </label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-gray-300 text-sm font-medium mb-2">
            Address
          </label>
          <textarea
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            rows={3}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            placeholder="Full address including city and state"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-2 border border-gray-600 text-gray-300 rounded-lg font-medium hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isLoading}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              isLoading
                ? 'bg-gray-600 cursor-not-allowed text-gray-400'
                : 'bg-orange-500 hover:bg-orange-600 text-white'
            }`}
          >
            {isLoading ? 'Creating User...' : 'Create User & Virtual Account'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateUserForm;
