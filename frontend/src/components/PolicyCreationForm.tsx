'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';
import usePolicyStore from '@/store/policyStore';

interface PolicyFormData {
  policy_name: string;
  policy_number: string;
  policy_type: string;
  start_date: string;
  due_date: string;
  duration_months: number;
  premium_amount: number;
  payment_frequency: string;
  first_payment_date: string;
  grace_period_days: number;
  company_name: string;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  rc_number: string;
  bvn: string;
  broker: string;
  coverage_amount: number;
  coverage_items: string;
  beneficiaries: string;
  broker_notes: string;
  internal_tags: string;
  auto_renew: boolean;
  notify_broker_on_change: boolean;
}

const PolicyCreationForm = () => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<PolicyFormData>({
    policy_name: '',
    policy_number: '',
    policy_type: 'LIFE',
    start_date: '',
    due_date: '',
    duration_months: 12,
    premium_amount: 0,
    payment_frequency: 'monthly',
    first_payment_date: '',
    grace_period_days: 30,
    company_name: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    rc_number: '',
    bvn: '',
    broker: '',
    coverage_amount: 0,
    coverage_items: '',
    beneficiaries: '',
    broker_notes: '',
    internal_tags: '',
    auto_renew: false,
    notify_broker_on_change: true,
  });

  const addPolicy = usePolicyStore((state) => state.addPolicy);

  // Fetch brokers for assignment
  const { data: brokers } = useQuery({
    queryKey: ['brokers'],
    queryFn: async () => {
      const response = await api.get('/brokers');
      return response.data;
    },
    retry: 1,
  });

  // Create policy mutation
  const createPolicyMutation = useMutation({
    mutationFn: async (data: PolicyFormData) => {
      const response = await api.post('/policies', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policies'] });
      alert('Policy created successfully!');
      // Reset form
      setFormData({
        policy_name: '',
        policy_number: '',
        policy_type: 'LIFE',
        start_date: '',
        due_date: '',
        duration_months: 12,
        premium_amount: 0,
        payment_frequency: 'monthly',
        first_payment_date: '',
        grace_period_days: 30,
        company_name: '',
        contact_person: '',
        contact_email: '',
        contact_phone: '',
        rc_number: '',
        bvn: '',
        broker: '',
        coverage_amount: 0,
        coverage_items: '',
        beneficiaries: '',
        broker_notes: '',
        internal_tags: '',
        auto_renew: false,
        notify_broker_on_change: true,
      });
    },
    onError: (error: any) => {
      alert(`Error creating policy: ${error.message}`);
    },
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createPolicyMutation.mutate(formData, {
      onSuccess: () => {
        // Add to local store as well
        const localPolicy = {
          ...formData,
          id: `${formData.policy_number || Math.random().toString(36).substr(2, 9)}-${Date.now()}`,
          created_at: new Date().toISOString(),
        };
        addPolicy(localPolicy);
      },
      onError: () => {
        // Add to local store even if backend fails
        const localPolicy = {
          ...formData,
          id: `${formData.policy_number || Math.random().toString(36).substr(2, 9)}-${Date.now()}`,
          created_at: new Date().toISOString(),
        };
        addPolicy(localPolicy);
      }
    });
  };

  const policyTypes = [
    { value: 'LIFE', label: 'Life Insurance' },
    { value: 'HEALTH', label: 'Health Insurance' },
    { value: 'AUTO', label: 'Auto Insurance' },
    { value: 'HOME', label: 'Home Insurance' },
    { value: 'BUSINESS', label: 'Business Insurance' },
    { value: 'TRAVEL', label: 'Travel Insurance' },
  ];

  const paymentFrequencies = [
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'annually', label: 'Annually' },
    { value: 'custom', label: 'Custom' },
  ];

  const brokerOptions = [
    { value: 'SCIB', label: 'SCIB' },
    { value: 'ARK_INSURANCE', label: 'ARK INSURANCE' },
    { value: 'IBN', label: 'IBN' },
  ];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Create New Policy</h1>
        <p className="text-gray-400">Comprehensive policy creation form with all required fields</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Policy Information */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Policy Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Policy Name *
              </label>
              <input
                type="text"
                name="policy_name"
                value={formData.policy_name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter policy name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Policy Number
              </label>
              <input
                type="text"
                name="policy_number"
                value={formData.policy_number}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Auto-generated or manual"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Policy Type *
              </label>
              <select
                name="policy_type"
                value={formData.policy_type}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                {policyTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Duration (Months)
              </label>
              <input
                type="number"
                name="duration_months"
                value={formData.duration_months}
                onChange={handleInputChange}
                min="1"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Start Date *
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Due Date *
              </label>
              <input
                type="date"
                name="due_date"
                value={formData.due_date}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              />
            </div>
          </div>
        </div>

        {/* Payment & Premium Details */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Payment & Premium Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Premium Amount (₦) *
              </label>
              <input
                type="number"
                name="premium_amount"
                value={formData.premium_amount}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Payment Frequency *
              </label>
              <select
                name="payment_frequency"
                value={formData.payment_frequency}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                {paymentFrequencies.map(freq => (
                  <option key={freq.value} value={freq.value}>
                    {freq.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                First Payment Date
              </label>
              <input
                type="date"
                name="first_payment_date"
                value={formData.first_payment_date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Grace Period (Days)
              </label>
              <input
                type="number"
                name="grace_period_days"
                value={formData.grace_period_days}
                onChange={handleInputChange}
                min="0"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              />
            </div>
          </div>
        </div>

        {/* Policyholder Information */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Policyholder Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Individual/Company Name *
              </label>
              <input
                type="text"
                name="company_name"
                value={formData.company_name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter individual or company name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Contact Person *
              </label>
              <input
                type="text"
                name="contact_person"
                value={formData.contact_person}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter contact person name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                name="contact_email"
                value={formData.contact_email}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter email address"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                name="contact_phone"
                value={formData.contact_phone}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter phone number"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                RC Number / Tax ID
              </label>
              <input
                type="text"
                name="rc_number"
                value={formData.rc_number}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter RC number or tax ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                BVN
              </label>
              <input
                type="text"
                name="bvn"
                value={formData.bvn}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter BVN"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Broker *
              </label>
              <select
                name="broker"
                value={formData.broker}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                <option value="">Select a Broker</option>
                {brokerOptions.map(broker => (
                  <option key={broker.value} value={broker.value}>
                    {broker.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Coverage Details */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Coverage Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Coverage Amount (₦) *
              </label>
              <input
                type="number"
                name="coverage_amount"
                value={formData.coverage_amount}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="0.00"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Coverage Items / Risk Type
              </label>
              <textarea
                name="coverage_items"
                value={formData.coverage_items}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Describe coverage items and risk types"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Beneficiaries
              </label>
              <textarea
                name="beneficiaries"
                value={formData.beneficiaries}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="List beneficiaries with their relationships and percentage shares"
              />
            </div>
          </div>
        </div>

        {/* Tags / Broker Visibility */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Tags / Broker Visibility</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Broker Notes
              </label>
              <textarea
                name="broker_notes"
                value={formData.broker_notes}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Add broker-specific notes"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Internal Tags
              </label>
              <input
                type="text"
                name="internal_tags"
                value={formData.internal_tags}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                placeholder="Enter tags separated by commas"
              />
            </div>
          </div>
        </div>

        {/* Optional Advanced Settings */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Optional Advanced Settings</h2>
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                name="auto_renew"
                checked={formData.auto_renew}
                onChange={handleInputChange}
                className="h-4 w-4 text-orange-500 focus:ring-orange-500 border-gray-600 rounded bg-gray-700"
              />
              <label className="ml-2 block text-sm text-gray-300">
                Auto-Renew Policy
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="notify_broker_on_change"
                checked={formData.notify_broker_on_change}
                onChange={handleInputChange}
                className="h-4 w-4 text-orange-500 focus:ring-orange-500 border-gray-600 rounded bg-gray-700"
              />
              <label className="ml-2 block text-sm text-gray-300">
                Notify Broker on Policy Changes
              </label>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="px-6 py-2 border border-gray-600 rounded-lg text-gray-300 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-500 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createPolicyMutation.isPending}
            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50 transition-colors"
          >
            {createPolicyMutation.isPending ? 'Creating...' : 'Create Policy'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PolicyCreationForm; 