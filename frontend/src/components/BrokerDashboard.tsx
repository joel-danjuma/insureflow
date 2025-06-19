'use client';

import React from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';

type ClientPortfolioItem = {
    clientName: string;
    policyType: string;
    policyStatus: 'Active' | 'Pending';
    premiumAmount: string;
    nextPaymentDate: string;
};

const mockPortfolio: ClientPortfolioItem[] = [
    { clientName: 'Lucas Bennett', policyType: 'Auto Insurance', policyStatus: 'Active', premiumAmount: '$1,200', nextPaymentDate: '2024-08-15' },
    { clientName: 'Sophia Carter', policyType: 'Home Insurance', policyStatus: 'Active', premiumAmount: '$1,500', nextPaymentDate: '2024-09-01' },
    { clientName: 'Owen Davis', policyType: 'Life Insurance', policyStatus: 'Pending', premiumAmount: '$2,000', nextPaymentDate: '2024-07-20' },
    { clientName: 'Chloe Foster', policyType: 'Health Insurance', policyStatus: 'Active', premiumAmount: '$1,800', nextPaymentDate: '2024-08-05' },
];

const portfolioColumns: ColumnDef<ClientPortfolioItem>[] = [
    { accessorKey: 'clientName', header: 'Client Name' },
    { accessorKey: 'policyType', header: 'Policy Type' },
    { 
        accessorKey: 'policyStatus', 
        header: 'Policy Status',
        cell: ({ row }) => {
            const isActive = row.original.policyStatus === 'Active';
            return (
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${isActive ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {row.original.policyStatus}
                </span>
            )
        }
    },
    { accessorKey: 'premiumAmount', header: 'Premium Amount' },
    { accessorKey: 'nextPaymentDate', header: 'Next Payment Date' },
];

const BrokerDashboard = () => {
  return (
    <>
      <div className="flex flex-wrap justify-between gap-3 pb-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight">Broker Dashboard</p>
          <p className="text-[#5c738a] text-sm font-normal leading-normal">Overview of your performance and client portfolio</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <MetricCard title="Total Sales" value="$250,000" change="+10%" />
        <MetricCard title="Client Retention Rate" value="95%" change="-2%" changeColor="text-red-500" />
        <MetricCard title="Average Commission" value="$5,000" change="+5%" />
      </div>

      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-5 pb-3">Sales Performance</h2>
      <div className="flex flex-wrap gap-4">
        {/* Placeholder for Sales Performance charts */}
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
            <p>Sales Over Time</p>
            <p className="text-3xl font-bold">$250,000</p>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
            <p>Sales by Product</p>
            <p className="text-3xl font-bold">$100,000</p>
        </div>
      </div>
      
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Client Portfolio</h2>
      <div className="w-full overflow-hidden rounded-xl border border-[#d4dbe2] bg-white">
        <DataTable columns={portfolioColumns} data={mockPortfolio} />
      </div>
    </>
  );
};

export default BrokerDashboard; 