'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { useQuery } from '@tanstack/react-query';
import api from '@/services/api';

interface Commission {
  id: number;
  policy_number: string;
  client_name: string;
  premium_amount: number;
  commission_rate: number;
  commission_amount: number;
  payment_date: string;
  status: 'paid' | 'pending' | 'processing';
  payment_method: string;
  transaction_ref: string;
}

const CommissionsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'paid' | 'pending' | 'processing'>('all');

  // Mock data - replace with actual API call
  const { data: commissions = [], isLoading } = useQuery({
    queryKey: ['commissions'],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return [
        {
          id: 1,
          policy_number: 'POL-2024-001',
          client_name: 'John Doe',
          premium_amount: 150000,
          commission_rate: 0.15,
          commission_amount: 22500,
          payment_date: '2024-01-15',
          status: 'paid' as const,
          payment_method: 'Bank Transfer',
          transaction_ref: 'TXN-001-2024',
        },
        {
          id: 2,
          policy_number: 'POL-2024-002',
          client_name: 'Jane Smith',
          premium_amount: 95000,
          commission_rate: 0.15,
          commission_amount: 14250,
          payment_date: '2024-01-20',
          status: 'paid' as const,
          payment_method: 'Bank Transfer',
          transaction_ref: 'TXN-002-2024',
        },
        {
          id: 3,
          policy_number: 'POL-2024-003',
          client_name: 'Mike Johnson',
          premium_amount: 50000,
          commission_rate: 0.15,
          commission_amount: 7500,
          payment_date: '',
          status: 'pending' as const,
          payment_method: 'Pending',
          transaction_ref: '',
        },
        {
          id: 4,
          policy_number: 'POL-2024-004',
          client_name: 'Sarah Wilson',
          premium_amount: 75000,
          commission_rate: 0.15,
          commission_amount: 11250,
          payment_date: '',
          status: 'processing' as const,
          payment_method: 'Processing',
          transaction_ref: 'TXN-004-2024',
        },
        {
          id: 5,
          policy_number: 'POL-2024-005',
          client_name: 'David Brown',
          premium_amount: 120000,
          commission_rate: 0.15,
          commission_amount: 18000,
          payment_date: '2024-01-18',
          status: 'paid' as const,
          payment_method: 'Bank Transfer',
          transaction_ref: 'TXN-005-2024',
        },
      ];
    },
  });

  const columns: ColumnDef<Commission>[] = [
    {
      accessorKey: 'policy_number',
      header: 'Policy Number',
      cell: ({ row }) => (
        <div className="font-medium text-white">{row.original.policy_number}</div>
      ),
    },
    {
      accessorKey: 'client_name',
      header: 'Client Name',
      cell: ({ row }) => (
        <div className="text-white">{row.original.client_name}</div>
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
      accessorKey: 'commission_rate',
      header: 'Commission Rate',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white font-medium">
            {(row.original.commission_rate * 100).toFixed(1)}%
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'commission_amount',
      header: 'Commission Amount',
      cell: ({ row }) => (
        <div className="text-right">
          <div className="text-white font-medium">
            ₦{(row.original.commission_amount / 1000).toFixed(1)}K
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'payment_date',
      header: 'Payment Date',
      cell: ({ row }) => (
        <div className="text-center">
          {row.original.payment_date ? (
            <div className="text-white">
              {new Date(row.original.payment_date).toLocaleDateString()}
            </div>
          ) : (
            <div className="text-gray-400">-</div>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const statusConfig = {
          paid: { bg: 'bg-green-900/30', text: 'text-green-400', border: 'border-green-500/30' },
          pending: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', border: 'border-yellow-500/30' },
          processing: { bg: 'bg-blue-900/30', text: 'text-blue-400', border: 'border-blue-500/30' },
        };
        const config = statusConfig[row.original.status];
        return (
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text} border ${config.border}`}>
            {row.original.status.charAt(0).toUpperCase() + row.original.status.slice(1)}
          </span>
        );
      },
    },
    {
      accessorKey: 'payment_method',
      header: 'Payment Method',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white">{row.original.payment_method}</div>
        </div>
      ),
    },
    {
      accessorKey: 'transaction_ref',
      header: 'Transaction Ref',
      cell: ({ row }) => (
        <div className="text-center">
          {row.original.transaction_ref ? (
            <div className="text-white text-sm">{row.original.transaction_ref}</div>
          ) : (
            <div className="text-gray-400 text-sm">-</div>
          )}
        </div>
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors">
            View
          </button>
          {row.original.status === 'paid' && (
            <button className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
              Download
            </button>
          )}
        </div>
      ),
    },
  ];

  const filteredCommissions = commissions.filter(commission => {
    const matchesSearch = commission.policy_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         commission.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         commission.transaction_ref.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || commission.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalCommission = commissions.reduce((sum, commission) => sum + commission.commission_amount, 0);
  const paidCommission = commissions.filter(c => c.status === 'paid').reduce((sum, commission) => sum + commission.commission_amount, 0);
  const pendingCommission = commissions.filter(c => c.status === 'pending').reduce((sum, commission) => sum + commission.commission_amount, 0);
  const processingCommission = commissions.filter(c => c.status === 'processing').reduce((sum, commission) => sum + commission.commission_amount, 0);

  if (isLoading) {
    return (
      <Layout title="Commissions">
        <div className="w-full p-4 lg:p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Commissions</h1>
            <p className="text-gray-400">View your commission earnings</p>
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
    <Layout title="Commissions">
      <div className="w-full p-4 lg:p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Commissions</h1>
          <p className="text-gray-400">View your commission earnings</p>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Search Commissions
              </label>
              <input
                type="text"
                placeholder="Search by policy number, client name, or transaction ref..."
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
                onChange={(e) => setStatusFilter(e.target.value as 'all' | 'paid' | 'pending' | 'processing')}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                <option value="all">All Commissions</option>
                <option value="paid">Paid</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
              </select>
            </div>
            <div className="flex items-end">
              <button className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 transition-colors">
                Request Payout
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Total Commission</p>
                <p className="text-2xl font-bold text-white">₦{(totalCommission / 1000).toFixed(1)}K</p>
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
                <p className="text-sm font-medium text-gray-400">Paid Commission</p>
                <p className="text-2xl font-bold text-white">₦{(paidCommission / 1000).toFixed(1)}K</p>
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
                <p className="text-sm font-medium text-gray-400">Pending Commission</p>
                <p className="text-2xl font-bold text-white">₦{(pendingCommission / 1000).toFixed(1)}K</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Processing Commission</p>
                <p className="text-2xl font-bold text-white">₦{(processingCommission / 1000).toFixed(1)}K</p>
              </div>
            </div>
          </div>
        </div>

        {/* Commissions Table */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <DataTable columns={columns} data={filteredCommissions} />
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(CommissionsPage); 