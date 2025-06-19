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
    { name: 'Ryan Kim', policiesSold: 220, commission: '$22,000', satisfaction: 78 },
    { name: 'Sophia Zhang', policiesSold: 180, commission: '$18,000', satisfaction: 88 },
    { name: 'Liam Davis', policiesSold: 150, commission: '$15,000', satisfaction: 80 },
];

const brokerColumns: ColumnDef<BrokerInfo>[] = [
    { accessorKey: 'name', header: 'Broker Name' },
    { accessorKey: 'policiesSold', header: 'Policies Sold' },
    { accessorKey: 'commission', header: 'Commission Earned' },
    { 
      accessorKey: 'satisfaction', 
      header: 'Client Satisfaction',
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
            <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2] h-1.5"><div className="h-full rounded-full bg-[#3f7fbf]" style={{ width: `${row.original.satisfaction}%` }}></div></div>
            <p className="text-[#101418] text-sm font-medium leading-normal">{row.original.satisfaction}</p>
        </div>
      )
    },
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
      <div className="flex flex-wrap justify-between gap-3 py-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight">Dashboard</p>
          <p className="text-[#5c738a] text-sm font-normal leading-normal">Overview of key metrics and performance indicators</p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="New Policies" value="1,250" change="+15%" />
        <MetricCard title="Outstanding Premiums" value="$750,000" change="-5%" changeColor="text-red-500" />
        <MetricCard title="Broker Performance" value="Top Broker: Ethan Carter" change="+10%" />
        <MetricCard title="Claims Processed" value="320" change="+8%" />
      </div>
      
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Broker Information</h2>
      <div className="w-full overflow-hidden rounded-xl border border-[#d4dbe2] bg-white">
        <DataTable columns={brokerColumns} data={mockBrokers} />
      </div>

      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Claims Data</h2>
      <div className="flex flex-wrap gap-4">
        {/* Placeholder for Claims Data charts */}
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
            <p>Claims Processed by Type</p>
            <p className="text-3xl font-bold">150</p>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
            <p>Claims Payout Over Time</p>
            <p className="text-3xl font-bold">$2.5M</p>
        </div>
      </div>
    </>
  );
};

export default InsuranceFirmDashboard; 