'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { clientService } from '@/services/api';
import ClientForm from '@/components/ClientForm';

interface Client {
  id: number;
  full_name: string;
  email: string;
  phone_number: string;
  company_name: string;
  total_policies: number;
  total_premium: number;
  last_contact: string;
  status: 'active' | 'inactive';
}

const ClientsPage = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedClientId, setSelectedClientId] = useState<number | undefined>(undefined);

  // Fetch clients from API
  const { data: clientsData = [], isLoading, refetch } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      try {
        const users = await clientService.getClients();
        // Transform user data to Client interface
        // For now, we'll set default values for total_policies, total_premium, etc.
        // In a real implementation, these would be calculated from policies
        return users.map((user: any) => ({
          id: user.id,
          full_name: user.full_name || '',
          email: user.email || '',
          phone_number: user.phone_number || '',
          company_name: user.organization_name || user.company_name || '',
          total_policies: 0, // TODO: Calculate from actual policies
          total_premium: 0, // TODO: Calculate from actual policies
          last_contact: user.created_at || new Date().toISOString(),
          status: (user.is_active ? 'active' : 'inactive') as 'active' | 'inactive',
        }));
      } catch (error) {
        console.error('Error fetching clients:', error);
        return [];
      }
    },
  });

  const clients = clientsData as Client[];

  const columns: ColumnDef<Client>[] = [
    {
      accessorKey: 'full_name',
      header: 'Client Name',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-white">{row.original.full_name}</div>
          <div className="text-sm text-gray-400">{row.original.company_name}</div>
        </div>
      ),
    },
    {
      accessorKey: 'email',
      header: 'Contact Information',
      cell: ({ row }) => (
        <div>
          <div className="text-white">{row.original.email}</div>
          <div className="text-sm text-gray-400">{row.original.phone_number}</div>
        </div>
      ),
    },
    {
      accessorKey: 'total_policies',
      header: 'Policies',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white font-medium">{row.original.total_policies}</div>
          <div className="text-sm text-gray-400">Active</div>
        </div>
      ),
    },
    {
      accessorKey: 'total_premium',
      header: 'Total Premium',
      cell: ({ row }) => (
        <div className="text-right">
          <div className="text-white font-medium">
            ₦{(row.original.total_premium / 1000000).toFixed(1)}M
          </div>
          <div className="text-sm text-gray-400">Annual</div>
        </div>
      ),
    },
    {
      accessorKey: 'last_contact',
      header: 'Last Contact',
      cell: ({ row }) => (
        <div className="text-center">
          <div className="text-white">{new Date(row.original.last_contact).toLocaleDateString()}</div>
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          row.original.status === 'active'
            ? 'bg-green-900/30 text-green-400 border border-green-500/30'
            : 'bg-red-900/30 text-red-400 border border-red-500/30'
        }`}>
          {row.original.status.charAt(0).toUpperCase() + row.original.status.slice(1)}
        </span>
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex space-x-2">
          <button 
            onClick={() => {
              setSelectedClientId(row.original.id);
              setModalMode('view');
              setShowModal(true);
            }}
            className="px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
          >
            View
          </button>
          <button 
            onClick={() => {
              setSelectedClientId(row.original.id);
              setModalMode('edit');
              setShowModal(true);
            }}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Edit
          </button>
        </div>
      ),
    },
  ];

  const filteredClients = clients.filter(client => {
    const matchesSearch = client.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.company_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || client.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (isLoading) {
    return (
      <Layout title="Clients">
        <div className="max-w-7xl mx-auto p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Clients</h1>
            <p className="text-gray-400">Manage your client relationships</p>
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
    <Layout title="Clients">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Clients</h1>
          <p className="text-gray-400">Manage your client relationships</p>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Search Clients
              </label>
              <input
                type="text"
                placeholder="Search by name, email, or company..."
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
                onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive')}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white"
              >
                <option value="all">All Clients</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <div className="flex items-end">
              <button 
                onClick={() => {
                  setSelectedClientId(undefined);
                  setModalMode('create');
                  setShowModal(true);
                }}
                className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 transition-colors"
              >
                Add New Client
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <svg className="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Total Clients</p>
                <p className="text-2xl font-bold text-white">{clients.length}</p>
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
                <p className="text-sm font-medium text-gray-400">Active Clients</p>
                <p className="text-2xl font-bold text-white">
                  {clients.filter(c => c.status === 'active').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Total Policies</p>
                <p className="text-2xl font-bold text-white">
                  {clients.reduce((sum, client) => sum + client.total_policies, 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-400">Total Premium</p>
                <p className="text-2xl font-bold text-white">
                  ₦{(clients.reduce((sum, client) => sum + client.total_premium, 0) / 1000000).toFixed(1)}M
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Clients Table */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <DataTable columns={columns} data={filteredClients} />
        </div>

        {/* Client Form Modal */}
        {showModal && (
          <ClientForm
            mode={modalMode}
            clientId={selectedClientId}
            onSuccess={(result) => {
              setShowModal(false);
              // Refetch clients list
              refetch();
              queryClient.invalidateQueries({ queryKey: ['clients'] });
            }}
            onCancel={() => {
              setShowModal(false);
              setSelectedClientId(undefined);
            }}
          />
        )}
      </div>
    </Layout>
  );
};

export default withAuth(ClientsPage); 