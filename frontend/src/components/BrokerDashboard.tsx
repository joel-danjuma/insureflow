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
];

const portfolioColumns: ColumnDef<ClientPortfolioItem>[] = [
    { accessorKey: 'clientName', header: 'Client Name' },
    { accessorKey: 'policyType', header: 'Policy Type' },
    { accessorKey: 'policyStatus', header: 'Policy Status' },
    { accessorKey: 'premiumAmount', header: 'Premium Amount' },
    { accessorKey: 'nextPaymentDate', header: 'Next Payment Date' },
];

const BrokerDashboard = () => {
  return (
    <>
      <h1 className="text-3xl font-bold mb-6">Broker Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <MetricCard title="Total Sales" value="$250,000" />
        <MetricCard title="Client Retention Rate" value="95%" />
        <MetricCard title="Average Commission" value="$5,000" />
      </div>
      <h2 className="text-2xl font-bold mb-4">Client Portfolio</h2>
      <DataTable columns={portfolioColumns} data={mockPortfolio} />
    </>
  );
};

export default BrokerDashboard; 