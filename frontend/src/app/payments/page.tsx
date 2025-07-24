'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { useQuery } from '@tanstack/react-query';
import api from '@/services/api';

interface Payment {
  id: number;
  policy_number: string;
  client_name: string;
  amount: number;
  payment_date: string;
  due_date: string;
  status: 'paid' | 'pending' | 'overdue' | 'failed';
  payment_method: string;
  transaction_ref: string;
}

const PaymentsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'paid' | 'pending' | 'overdue' | 'failed'>('all');

  // Mock data - replace with actual API call
  const { data: payments = [], isLoading } = useQuery({
    queryKey: ['payments'],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return [
        {
          id: 1,
          policy_number: 'POL-2024-001',
          client_name: 'John Doe',
          amount: 150000,
          payment_date: '2024-01-15',
          due_date: '2024-01-15',
          status: 'paid' as const,
          payment_method: 'Bank Transfer',
          transaction_ref: 'TXN-001-2024',
        },
        {
          id: 2,
          policy_number: 'POL-2024-002',
          client_name: 'Jane Smith',
          amount: 95000,
          payment_date: '2024-01-20',
          due_date: '2024-01-20',
          status: 'paid' as const,
          payment_method: 'Card Payment',
          transaction_ref: 'TXN-002-2024',
        },
        {
          id: 3,
          policy_number: 'POL-2024-003',
          client_name: 'Mike Johnson',
          amount: 50000,
          payment_date: '',
          due_date: '2024-01-25',
          status: 'pending' as const,
          payment_method: 'Pending',
          transaction_ref: '',
        },
        {
          id: 4,
          policy_number: 'POL-2024-004',
          client_name: 'Sarah Wilson',
          amount: 75000,
          payment_date: '',
          due_date: '2024-01-10',
          status: 'overdue' as const,
          payment_method: 'Pending',
          transaction_ref: '',
        },
        {
          id: 5,
          policy_number: 'POL-2024-005',
          client_name: 'David Brown',
          amount: 120000,
          payment_date: '',
          due_date: '2024-01-18',
          status: 'failed' as const,
          payment_method: 'Card Payment',
          transaction_ref: 'TXN-005-2024',
        },
      ];
    },
  });

  const columns: ColumnDef<Payment>[] = [
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
      accessorKey: 'amount',
      header: 'Amount',
      cell: ({ row }) => (
        <div className="text-right">
          <div className="text-white font-medium">
            ₦{(row.original.amount / 1000).toFixed(0)}K
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
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const statusConfig = {
          paid: { bg: 'bg-green-900/30', text: 'text-green-400', border: 'border-green-500/30' },
          pending: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', border: 'border-yellow-500/30' },
          overdue: { bg: 'bg-red-900/30', text: 'text-red-400', border: 'border-red-500/30' },
          failed: { bg: 'bg-gray-900/30', text: 'text-gray-400', border: 'border-gray-500/30' },
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
          {row.original.status === 'pending' && (
            <button className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
              Mark Paid
            </button>
          )}
        </div>
      ),
    },
  ];

  const filteredPayments = payments.filter(payment => {
    const matchesSearch = payment.policy_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         payment.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         payment.transaction_ref.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || payment.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalAmount = payments.reduce((sum, payment) => sum + payment.amount, 0);
  const paidAmount = payments.filter(p => p.status === 'paid').reduce((sum, payment) => sum + payment.amount, 0);
  const pendingAmount = payments.filter(p => p.status === 'pending').reduce((sum, payment) => sum + payment.amount, 0);
  const overdueAmount = payments.filter(p => p.status === 'overdue').reduce((sum, payment) => sum + payment.amount, 0);

  if (isLoading) {
    return (
      <Layout title="Payments">
        <div className="max-w-7xl mx-auto p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Payments</h1>
            <p className="text-gray-400">Manage payment transactions</p>
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
    <Layout title="Payments">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Payments</h1>
          <p className="text-gray-400">Manage payment transactions</p>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Search Payments
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
                onChange={(e) => setStatusFilter(e.target.value as 'all' | 'paid' | 'pending' | 'overdue' | 'failed')}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                <option value="all">All Payments</option>
                <option value="paid">Paid</option>
                <option value="pending">Pending</option>
                <option value="overdue">Overdue</option>
                <option value="failed">Failed</option>
              </select>
            </div>
            <div className="flex items-end">
              <button className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 transition-colors">
                Record Payment
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Total Amount</p>
                <p className="text-2xl font-bold text-white">₦{(totalAmount / 1000).toFixed(0)}K</p>
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
                <p className="text-sm font-medium text-gray-400">Paid Amount</p>
                <p className="text-2xl font-bold text-white">₦{(paidAmount / 1000).toFixed(0)}K</p>
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
                <p className="text-sm font-medium text-gray-400">Pending Amount</p>
                <p className="text-2xl font-bold text-white">₦{(pendingAmount / 1000).toFixed(0)}K</p>
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
                <p className="text-sm font-medium text-gray-400">Overdue Amount</p>
                <p className="text-2xl font-bold text-white">₦{(overdueAmount / 1000).toFixed(0)}K</p>
              </div>
            </div>
          </div>
        </div>

        {/* Payments Table */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <DataTable columns={columns} data={filteredPayments} />
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(PaymentsPage); 