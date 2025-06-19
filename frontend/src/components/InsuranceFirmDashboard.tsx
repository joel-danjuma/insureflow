'use client';

import React from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
// We will mock the data for now
// import useQuery from '@/hooks/useQuery';
// import apiClient from '@/services/api';

type BrokerInfo = {
  name: string;
  policiesSold: number;
  commission: string;
  satisfaction: number;
};

const mockBrokers: BrokerInfo[] = [
    { name: 'Ethan Carter', policiesSold: 350, commission: '$35,000', satisfaction: 85 },
    { name: 'Isabella Rossi', policiesSold: 280, commission: '$28,000', satisfaction: 92 },
];

const brokerColumns: ColumnDef<BrokerInfo>[] = [
    { accessorKey: 'name', header: 'Broker Name' },
    { accessorKey: 'policiesSold', header: 'Policies Sold' },
    { accessorKey: 'commission', header: 'Commission Earned' },
    { accessorKey: 'satisfaction', header: 'Client Satisfaction' },
];

const InsuranceFirmDashboard = () => {
  // const { data, isLoading, error } = useQuery(fetchAdminData);
  // For now, we use static data to build the UI.
  const isLoading = false;
  const error = null;

  if (isLoading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error: An unexpected error occurred.</div>;

  return (
    <>
      <h1 className="text-3xl font-bold mb-6">Insurance Firm Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard title="New Policies" value="1,250" />
        <MetricCard title="Outstanding Premiums" value="$750,000" />
        <MetricCard title="Broker Performance" value="Ethan Carter" />
        <MetricCard title="Claims Processed" value="320" />
      </div>
      <h2 className="text-2xl font-bold mb-4">Broker Information</h2>
      <DataTable columns={brokerColumns} data={mockBrokers} />
    </>
  );
};

export default InsuranceFirmDashboard; 