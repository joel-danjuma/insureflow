'use client';

import React from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import useQuery from '@/hooks/useQuery';
import apiClient from '@/services/api';

// This would come from your backend schemas
type Policy = {
    id: string;
    policy_number: string;
    user: { full_name: string };
    status: string;
    premium: number;
};
  
const columns: ColumnDef<Policy>[] = [
    { accessorKey: 'policy_number', header: 'Policy #' },
    { accessorKey: 'user.full_name', header: 'Holder' },
    { accessorKey: 'status', header: 'Status' },
    {
        accessorKey: 'premium',
        header: 'Premium',
        cell: ({ row }) => `$${row.original.premium.toFixed(2)}`,
    },
];

const fetchBrokerData = async () => {
  // The backend will scope this data based on the authenticated user's token
  const kpis = await apiClient.get('/dashboard/kpis');
  const policies = await apiClient.get('/dashboard/recent-policies');
  return { kpis: kpis.data, policies: policies.data };
};

const BrokerDashboard = () => {
  const { data, isLoading, error } = useQuery(fetchBrokerData);

  if (isLoading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Broker Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <MetricCard title="New Policies (Month)" value={data?.kpis.new_policies_this_month || 0} />
        <MetricCard title="Outstanding Premiums" value={`$${(data?.kpis.outstanding_premiums_total || 0).toFixed(2)}`} />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Your Recent Policies</h2>
        <DataTable columns={columns} data={data?.policies || []} />
      </div>
    </div>
  );
};

export default BrokerDashboard; 