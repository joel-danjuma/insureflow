'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { useQuery } from '@tanstack/react-query';
import api from '@/services/api';

interface CustomerPolicy {
  id: number;
  policy_number: string;
  policy_type: string;
  premium_amount: number;
  coverage_amount: number;
  start_date: string;
  due_date: string;
  payment_status: 'paid' | 'pending' | 'overdue';
  next_payment_date: string;
  broker_name: string;
}

const MyPoliciesPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'paid' | 'pending' | 'overdue'>('all');

  // Mock data - replace with actual API call
  const { data: policies = [], isLoading } = useQuery({
    queryKey: ['my-policies'],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return [
        {
          id: 1,
          policy_number: 'POL-2024-001',
          policy_type: 'Life Insurance',
          premium_amount: 150000,
          coverage_amount: 5000000,
          start_date: '2024-01-01',
          due_date: '2024-12-31',
          payment_status: 'paid' as const,
          next_payment_date: '2024-02-01',
          broker_name: 'John Broker',
        },
        {
          id: 2,
          policy_number: 'POL-2024-002',
          policy_type: 'Auto Insurance',
          premium_amount: 95000,
          coverage_amount: 2000000,
          start_date: '2024-01-15',
          due_date: '2025-01-14',
          payment_status: 'pending' as const,
          next_payment_date: '2024-02-15',
          broker_name: 'Jane Broker',
        },
        {
          id: 3,
          policy_number: 'POL-2024-003',
          policy_type: 'Health Insurance',
          premium_amount: 50000,
          coverage_amount: 1000000,
          start_date: '2024-01-10',
          due_date: '2024-12-09',
          payment_status: 'overdue' as const,
          next_payment_date: '2024-02-10',
          broker_name: 'Mike Broker',
        },
        {
          id: 4,
          policy_number: 'POL-2024-004',
          policy_type: 'Home Insurance',
          premium_amount: 75000,
          coverage_amount: 3000000,
          start_date: '2024-01-20',
          due_date: '2025-01-19',
          payment_status: 'paid' as const,
          next_payment_date: '2024-02-20',
          broker_name: 'Sarah Broker',
        },
      ];
    },
  });

  const columns: ColumnDef<CustomerPolicy>[] = [
    {
      accessorKey: 'policy_number',
      header: 'Policy Number',
      cell: ({ row }) => (
        <div className="font-medium text-white">{row.original.policy_number}</div>
      ),
    },
    {
      accessorKey: 'policy_type',
      header: 'Policy Type',
      cell: ({ row }) => (
        <div className="text-white">{row.original.policy_type}</div>
      ),
    },
    {
      accessorKey: 'premium_amount',
      header: 'Premium Amount',
      cell: ({ row }) => (
        <div className="text-right">
          <div className="text-white font-medium">
            ₦{(row.original.premium_amount / 1000).toFixed(0)}K
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'coverage_amount',
      header: 'Coverage Amount',
      cell: ({ row }) => (
        <div className="text-right">
          <div className="text-white font-medium">
            ₦{(row.original.coverage_amount / 1000000).toFixed(1)}M
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'start_date',
      header: 'Start Date',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white">
            {new Date(row.original.start_date).toLocaleDateString()}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'due_date',
      header: 'Due Date',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white">
            {new Date(row.original.due_date).toLocaleDateString()}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'payment_status',
      header: 'Payment Status',
      cell: ({ row }) => {
        const statusConfig = {
          paid: { bg: 'bg-green-900/30', text: 'text-green-400', border: 'border-green-500/30' },
          pending: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', border: 'border-yellow-500/30' },
          overdue: { bg: 'bg-red-900/30', text: 'text-red-400', border: 'border-red-500/30' },
        };
        const config = statusConfig[row.original.payment_status];
        return (
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text} border ${config.border}`}>
            {row.original.payment_status.charAt(0).toUpperCase() + row.original.payment_status.slice(1)}
          </span>
        );
      },
    },
    {
      accessorKey: 'next_payment_date',
      header: 'Next Payment',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white">
            {new Date(row.original.next_payment_date).toLocaleDateString()}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'broker_name',
      header: 'Broker',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white">{row.original.broker_name}</div>
        </div>
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors">
            View Details
          </button>
          {row.original.payment_status === 'pending' && (
            <button className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
              Make Payment
            </button>
          )}
        </div>
      ),
    },
  ];

  const filteredPolicies = policies.filter(policy => {
    const matchesSearch = policy.policy_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         policy.policy_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         policy.broker_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || policy.payment_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalPolicies = policies.length;
  const activePolicies = policies.filter(p => p.payment_status === 'paid').length;
  const pendingPayments = policies.filter(p => p.payment_status === 'pending').length;
  const overduePayments = policies.filter(p => p.payment_status === 'overdue').length;

  if (isLoading) {
    return (
      <Layout title="My Policies">
        <div className="max-w-7xl mx-auto p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">My Policies</h1>
            <p className="text-gray-400">View your insurance policies</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-700 rounded w-1/4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="My Policies">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">My Policies</h1>
          <p className="text-gray-400">View your insurance policies</p>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Search Policies
              </label>
              <input
                type="text"
                placeholder="Search by policy number, type, or broker..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Status Filter
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as 'all' | 'paid' | 'pending' | 'overdue')}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                <option value="all">All Policies</option>
                <option value="paid">Active</option>
                <option value="pending">Pending Payment</option>
                <option value="overdue">Overdue</option>
              </select>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Total Policies</p>
                <p className="text-2xl font-bold text-white">{totalPolicies}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Active Policies</p>
                <p className="text-2xl font-bold text-white">{activePolicies}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-500/20 rounded-lg">
                <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Pending Payments</p>
                <p className="text-2xl font-bold text-white">{pendingPayments}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Overdue Payments</p>
                <p className="text-2xl font-bold text-white">{overduePayments}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Policies Table */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <DataTable columns={columns} data={filteredPolicies} />
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(MyPoliciesPage); 