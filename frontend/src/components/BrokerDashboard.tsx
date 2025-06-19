'use client';

import React, { useState, useMemo } from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { paymentService } from '@/services/api';

type ClientPortfolioItem = {
    id: number;
    clientName: string;
    policyType: string;
    policyStatus: 'Active' | 'Pending';
    premiumAmount: number;
    nextPaymentDate: string;
};

const mockPortfolio: ClientPortfolioItem[] = [
    { id: 1, clientName: 'Lucas Bennett', policyType: 'Auto Insurance', policyStatus: 'Active', premiumAmount: 1200, nextPaymentDate: '2024-08-15' },
    { id: 2, clientName: 'Sophia Carter', policyType: 'Home Insurance', policyStatus: 'Active', premiumAmount: 1500, nextPaymentDate: '2024-09-01' },
    { id: 3, clientName: 'Owen Davis', policyType: 'Life Insurance', policyStatus: 'Pending', premiumAmount: 2000, nextPaymentDate: '2024-07-20' },
    { id: 4, clientName: 'Chloe Foster', policyType: 'Health Insurance', policyStatus: 'Active', premiumAmount: 1800, nextPaymentDate: '2024-08-05' },
];

const portfolioColumns: ColumnDef<ClientPortfolioItem>[] = [
    {
        id: 'select',
        header: ({ table }) => (
            <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                checked={table.getIsAllPageRowsSelected()}
                onChange={(value) => table.toggleAllPageRowsSelected(!!value.target.checked)}
                aria-label="Select all"
            />
        ),
        cell: ({ row }) => (
            <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                checked={row.getIsSelected()}
                onChange={(value) => row.toggleSelected(!!value.target.checked)}
                aria-label="Select row"
            />
        ),
        enableSorting: false,
        enableHiding: false,
    },
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
    { accessorKey: 'premiumAmount', header: 'Premium Amount', cell: ({ row }) => `$${row.original.premiumAmount.toFixed(2)}` },
    { accessorKey: 'nextPaymentDate', header: 'Next Payment Date' },
];

const BrokerDashboard = () => {
    const [selectedPolicies, setSelectedPolicies] = useState<ClientPortfolioItem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const totalSelectedAmount = useMemo(() => {
        return selectedPolicies.reduce((sum, policy) => sum + policy.premiumAmount, 0);
    }, [selectedPolicies]);

    const handlePaySelected = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const policyIds = selectedPolicies.map(p => p.id);
            const response = await paymentService.initiateBulkPayment(policyIds);
            // Redirect to the payment URL provided by the backend
            if (response.payment_url) {
                window.location.href = response.payment_url;
            } else {
                throw new Error('No payment URL received from server.');
            }
        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('An unknown error occurred.');
            }
        } finally {
            setIsLoading(false);
        }
    };

  return (
    <>
      <div className="flex flex-wrap justify-between gap-3 pb-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-foreground tracking-light text-[32px] font-bold leading-tight">Broker Dashboard</p>
          <p className="text-foreground/70 text-sm font-normal leading-normal">Overview of your performance and client portfolio</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <MetricCard title="Total Sales" value="$250,000" change="+10%" />
        <MetricCard title="Client Retention Rate" value="95%" change="-2%" changeColor="text-red-500" />
        <MetricCard title="Average Commission" value="$5,000" change="+5%" />
      </div>

      <h2 className="text-foreground text-[22px] font-bold leading-tight tracking-[-0.015em] pt-5 pb-3">Sales Performance</h2>
      <div className="flex flex-wrap gap-4">
        {/* Placeholder for Sales Performance charts */}
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border p-6">
            <p>Sales Over Time</p>
            <p className="text-3xl font-bold">$250,000</p>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border p-6">
            <p>Sales by Product</p>
            <p className="text-3xl font-bold">$100,000</p>
        </div>
      </div>
      
      <h2 className="text-foreground text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Client Portfolio</h2>
      
      <div className="flex justify-end mb-4">
        <button 
            onClick={handlePaySelected}
            disabled={selectedPolicies.length === 0 || isLoading}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 disabled:bg-slate-400 disabled:cursor-not-allowed"
        >
            {isLoading ? 'Processing...' : `Pay for Selected (${selectedPolicies.length}) - $${totalSelectedAmount.toFixed(2)}`}
        </button>
      </div>
      {error && <p className="text-sm text-red-600 my-2 text-right">{error}</p>}

      <div className="w-full overflow-hidden rounded-xl border border-border bg-card">
        <DataTable columns={portfolioColumns} data={mockPortfolio} onRowSelectionChange={setSelectedPolicies} />
      </div>
    </>
  );
};

export default BrokerDashboard; 