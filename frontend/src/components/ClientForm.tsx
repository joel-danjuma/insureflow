'use client';

import React, { useState, useEffect } from 'react';
import { clientService } from '@/services/api';

interface ClientFormProps {
  mode: 'create' | 'edit' | 'view';
  clientId?: number;
  onSuccess?: (result: any) => void;
  onCancel?: () => void;
}

interface FormData {
  email: string;
  full_name: string;
  username: string;
  phone_number: string;
  company_name: string;
  date_of_birth: string;
  gender: string;
  address: string;
}

const ClientForm: React.FC<ClientFormProps> = ({ mode, clientId, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    full_name: '',
    username: '',
    phone_number: '',
    company_name: '',
    date_of_birth: '',
    gender: '',
    address: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);

  // Load client data if in edit or view mode
  useEffect(() => {
    if ((mode === 'edit' || mode === 'view') && clientId) {
      setIsLoadingData(true);
      clientService.getClient(clientId)
        .then(client => {
          setFormData({
            email: client.email || '',
            full_name: client.full_name || '',
            username: client.username || '',
            phone_number: client.phone_number || '',
            company_name: client.company_name || client.organization_name || '',
            date_of_birth: client.date_of_birth || '',
            gender: client.gender || '',
            address: client.address || '',
          });
        })
        .catch(err => {
          setError('Failed to load client data. Please try again.');
          console.error('Error loading client:', err);
        })
        .finally(() => {
          setIsLoadingData(false);
        });
    }
  }, [mode, clientId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (mode === 'view') {
      onCancel?.();
      return;
    }

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
      if (!cleanedData.email || !cleanedData.full_name) {
        setError('Email and Full Name are required fields.');
        return;
      }

      let result;
      if (mode === 'create') {
        // Generate username from email if not provided
        if (!cleanedData.username) {
          cleanedData.username = cleanedData.email.split('@')[0];
        }
        result = await clientService.createClient(cleanedData);
      } else if (mode === 'edit' && clientId) {
        result = await clientService.updateClient(clientId, cleanedData);
      }
      
      if (onSuccess && result) {
        onSuccess(result);
      }
    } catch (err: any) {
      console.error(`Error ${mode === 'create' ? 'creating' : 'updating'} client:`, err);
      setError(err.response?.data?.detail || err.message || `Failed to ${mode === 'create' ? 'create' : 'update'} client. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  const isReadOnly = mode === 'view';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-white text-xl font-bold">
            {mode === 'create' ? 'Create New Client' : mode === 'edit' ? 'Edit Client' : 'Client Details'}
          </h3>
          {onCancel && (
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-white transition-colors text-2xl"
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

        {isLoadingData ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          </div>
        ) : (
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
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
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
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="John Doe"
                />
              </div>

              {mode === 'create' && (
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    disabled={isReadOnly}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                    placeholder="Auto-generated from email"
                  />
                </div>
              )}

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="+234 801 234 5678"
                />
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="ABC Company"
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
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
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
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
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
                disabled={isReadOnly}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
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
                  {mode === 'view' ? 'Close' : 'Cancel'}
                </button>
              )}
              {mode !== 'view' && (
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    isLoading
                      ? 'bg-gray-600 cursor-not-allowed text-gray-400'
                      : 'bg-orange-500 hover:bg-orange-600 text-white'
                  }`}
                >
                  {isLoading 
                    ? (mode === 'create' ? 'Creating Client...' : 'Updating Client...')
                    : (mode === 'create' ? 'Create Client' : 'Update Client')
                  }
                </button>
              )}
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ClientForm;
