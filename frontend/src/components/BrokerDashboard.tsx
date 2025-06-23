'use client';

import React, { useState, useMemo } from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { formatNaira } from '@/utils/currency';
import { useBrokerProfile, usePolicies, usePremiums } from '@/hooks/useQuery';
import { Policy, Premium } from '@/types/user';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { paymentService, premiumService } from '@/services/api';

type ClientPortfolioItem = {
    id: string;
    policyId: number;
    premiumId: number | null;
    clientName: string;
    policyType: string;
    policyStatus: 'Active' | 'Pending';
    paymentStatus: 'Paid' | 'Pending' | 'Overdue';
    premiumAmount: string;
    premiumAmountRaw: number;
    nextPaymentDate: string;
};

const BrokerDashboard = () => {
  const { data: brokerProfile, isLoading: brokerLoading, error: brokerError } = useBrokerProfile();
  const { data: policies, isLoading: policiesLoading, error: policiesError } = usePolicies();
  const { data: premiums, isLoading: premiumsLoading, error: premiumsError } = usePremiums();

  // State for selected policies
  const [selectedPolicies, setSelectedPolicies] = useState<Set<string>>(new Set());
  const [paymentLoading, setPaymentLoading] = useState<Set<string>>(new Set());
  const [bulkPaymentLoading, setBulkPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState<string | null>(null);

  // Clear messages after 5 seconds
  React.useEffect(() => {
    if (paymentError || paymentSuccess) {
      const timer = setTimeout(() => {
        setPaymentError(null);
        setPaymentSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [paymentError, paymentSuccess]);

  // Calculate broker metrics from data
  const calculateBrokerMetrics = (policies: Policy[], premiums: Premium[]) => {
    const totalSales = policies.reduce((sum, policy) => sum + policy.premium_amount, 0);
    const totalCommission = totalSales * 0.15; // 15% commission rate
    const activeClients = new Set(policies.map(p => p.customer_id)).size;
    const retentionRate = policies.length > 0 ? Math.round((activeClients / policies.length) * 100) : 0;
    
    return {
      totalSales,
      totalCommission,
      retentionRate,
      activeClients,
    };
  };

  // Transform policies into client portfolio with payment status
  const transformToClientPortfolio = (policies: Policy[]): ClientPortfolioItem[] => {
    return policies.map(policy => {
      const nextPaymentDate = new Date(policy.end_date);
      const today = new Date();
      const daysDiff = Math.ceil((nextPaymentDate.getTime() - today.getTime()) / (1000 * 3600 * 24));
      
      let paymentStatus: 'Paid' | 'Pending' | 'Overdue' = 'Pending';
      if (daysDiff < 0) {
        paymentStatus = 'Overdue';
      } else if (policy.status === 'active' && daysDiff > 30) {
        paymentStatus = 'Paid';
      }

      // Find the corresponding premium for this policy
      const premium = premiums?.find(p => p.policy_id === policy.id);

      return {
        id: policy.id.toString(),
        policyId: policy.id,
        premiumId: premium?.id || null,
        clientName: policy.customer?.full_name || 'Unknown Client',
        policyType: policy.policy_type,
        policyStatus: policy.status === 'active' ? 'Active' : 'Pending',
        paymentStatus,
        premiumAmount: formatNaira(policy.premium_amount),
        premiumAmountRaw: policy.premium_amount,
        nextPaymentDate: nextPaymentDate.toLocaleDateString('en-GB'),
      };
    });
  };

  const clientPortfolio = useMemo(() => 
    transformToClientPortfolio(policies || []), 
    [policies, premiums]
  );

  // Handle individual row selection
  const handleRowSelection = (policyId: string, isSelected: boolean) => {
    const newSelected = new Set(selectedPolicies);
    if (isSelected) {
      newSelected.add(policyId);
    } else {
      newSelected.delete(policyId);
    }
    setSelectedPolicies(newSelected);
  };

  // Handle select all
  const handleSelectAll = (isSelected: boolean) => {
    if (isSelected) {
      setSelectedPolicies(new Set(clientPortfolio.map(item => item.id)));
    } else {
      setSelectedPolicies(new Set());
    }
  };

  // Handle individual premium payment
  const handleSinglePayment = async (premiumId: number, policyId: string) => {
    if (!premiumId) {
      setPaymentError('No premium found for this policy');
      return;
    }

    setPaymentLoading(prev => new Set(prev).add(policyId));
    setPaymentError(null);
    setPaymentSuccess(null);

    try {
      const response = await premiumService.payPremium(premiumId);
      
      if (response.payment_url) {
        // Redirect to Squad Co payment page
        window.open(response.payment_url, '_blank');
        setPaymentSuccess(`Payment initiated for premium ${premiumId}. Complete payment in the new tab.`);
      } else {
        setPaymentError('No payment URL received from payment service');
      }
    } catch (error) {
      setPaymentError(error instanceof Error ? error.message : 'Failed to initiate payment');
    } finally {
      setPaymentLoading(prev => {
        const newSet = new Set(prev);
        newSet.delete(policyId);
        return newSet;
      });
    }
  };

  // Handle bulk payment
  const handleBulkPayment = async () => {
    const selectedPolicyIds = Array.from(selectedPolicies).map(id => parseInt(id));
    
    if (selectedPolicyIds.length === 0) {
      setPaymentError('No policies selected for payment');
      return;
    }

    setBulkPaymentLoading(true);
    setPaymentError(null);
    setPaymentSuccess(null);

    try {
      const response = await paymentService.initiateBulkPayment(selectedPolicyIds);
      
      if (response.payment_url) {
        // Redirect to Squad Co payment page
        window.open(response.payment_url, '_blank');
        setPaymentSuccess(`Bulk payment initiated for ${selectedPolicyIds.length} policies. Complete payment in the new tab.`);
        
        // Clear selection after successful initiation
        setSelectedPolicies(new Set());
      } else {
        setPaymentError('No payment URL received from payment service');
      }
    } catch (error) {
      setPaymentError(error instanceof Error ? error.message : 'Failed to initiate bulk payment');
    } finally {
      setBulkPaymentLoading(false);
    }
  };

  // Calculate selected policies totals
  const selectedPoliciesData = useMemo(() => {
    const selectedCount = selectedPolicies.size;
    const selectedTotal = clientPortfolio
      .filter(item => selectedPolicies.has(item.id))
      .reduce((sum, item) => sum + item.premiumAmountRaw, 0);
    
    return { selectedCount, selectedTotal };
  }, [selectedPolicies, clientPortfolio]);

  // Check if all policies are selected
  const isAllSelected = clientPortfolio.length > 0 && selectedPolicies.size === clientPortfolio.length;
  const isPartiallySelected = selectedPolicies.size > 0 && selectedPolicies.size < clientPortfolio.length;

  const portfolioColumns: ColumnDef<ClientPortfolioItem>[] = [
    {
      id: 'select',
      header: ({ table }) => (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={isAllSelected}
            ref={(el) => {
              if (el) el.indeterminate = isPartiallySelected;
            }}
            onChange={(e) => handleSelectAll(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
        </div>
      ),
      cell: ({ row }) => (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selectedPolicies.has(row.original.id)}
            onChange={(e) => handleRowSelection(row.original.id, e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
        </div>
      ),
      enableSorting: false,
    },
    { accessorKey: 'clientName', header: 'Client Name' },
    { accessorKey: 'policyType', header: 'Policy Type' },
    { 
      accessorKey: 'policyStatus', 
      header: 'Policy Status',
      cell: ({ row }) => {
        const isActive = row.original.policyStatus === 'Active';
        return (
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${isActive ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-yellow-100 text-yellow-800 border border-yellow-200'}`}>
            {row.original.policyStatus}
          </span>
        )
      }
    },
    {
      accessorKey: 'paymentStatus',
      header: 'Payment Status',
      cell: ({ row }) => {
        const status = row.original.paymentStatus;
        const statusColors = {
          'Paid': 'bg-green-100 text-green-800 border-green-200',
          'Pending': 'bg-yellow-100 text-yellow-800 border-yellow-200',
          'Overdue': 'bg-red-100 text-red-800 border-red-200'
        };
        
        return (
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${statusColors[status]}`}>
            {status}
          </span>
        );
      }
    },
    { accessorKey: 'premiumAmount', header: 'Premium Amount' },
    { accessorKey: 'nextPaymentDate', header: 'Next Payment Date' },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => {
        const item = row.original;
        const isLoading = paymentLoading.has(item.id);
        
        if (item.paymentStatus === 'Paid') {
          return (
            <span className="text-green-600 text-sm font-medium">Paid</span>
          );
        }
        
        return (
          <button
            onClick={() => handleSinglePayment(item.premiumId!, item.id)}
            disabled={!item.premiumId || isLoading}
            className={`px-3 py-1 text-sm font-medium rounded transition-colors ${
              !item.premiumId || isLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isLoading ? 'Processing...' : 'Pay Now'}
          </button>
        );
      },
      enableSorting: false,
    },
  ];

  if (brokerLoading || policiesLoading || premiumsLoading) {
    return (
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="flex flex-wrap justify-between gap-3 pb-4">
          <div className="flex min-w-72 flex-col gap-3">
            <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
          </div>
        </div>
        
        {/* Metric cards skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <MetricCard key={i} title="" value="" isLoading={true} />
          ))}
        </div>
        
        {/* Charts skeleton */}
        <div className="space-y-6">
          <div className="h-6 bg-gray-200 rounded w-48 animate-pulse"></div>
          <div className="flex flex-wrap gap-4">
            <div className="h-32 bg-gray-100 rounded-xl border border-gray-200 animate-pulse flex-1 min-w-72"></div>
            <div className="h-32 bg-gray-100 rounded-xl border border-gray-200 animate-pulse flex-1 min-w-72"></div>
          </div>
        </div>
        
        {/* Table skeleton */}
        <div className="space-y-6">
          <div className="h-6 bg-gray-200 rounded w-48 animate-pulse"></div>
          <div className="h-64 bg-gray-100 rounded-xl border border-gray-200 animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (brokerError || policiesError || premiumsError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center p-8 border border-red-200 rounded-lg bg-red-50">
          <div className="text-red-600 text-xl font-semibold mb-2">Error Loading Dashboard</div>
          <p className="text-red-500 mb-4">
            {(brokerError || policiesError || premiumsError)?.toString()}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const metrics = calculateBrokerMetrics(policies || [], premiums || []);

  // Mock chart data for sales performance
  const salesPerformanceData = [
    { month: 'Jan', sales: 45000000, policies: 12 },
    { month: 'Feb', sales: 52000000, policies: 14 },
    { month: 'Mar', sales: 48000000, policies: 13 },
    { month: 'Apr', sales: 61000000, policies: 16 },
    { month: 'May', sales: 55000000, policies: 15 },
    { month: 'Jun', sales: 70000000, policies: 18 },
  ];

  return (
    <>
      <div className="flex flex-wrap justify-between gap-3 pb-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight">
            {brokerProfile?.name || 'Broker'} Dashboard
          </p>
          <p className="text-[#5c738a] text-sm font-normal leading-normal">Overview of your performance and client portfolio</p>
        </div>
      </div>

      {/* Payment status messages */}
      {paymentError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="text-red-600 text-sm">
              <strong>Error:</strong> {paymentError}
            </div>
          </div>
        </div>
      )}

      {paymentSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="text-green-600 text-sm">
              <strong>Success:</strong> {paymentSuccess}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <MetricCard 
          title="Total Sales" 
          value={metrics.totalSales} 
          change={10} 
          changeType="increase" 
          isCurrency={true} 
        />
        <MetricCard 
          title="Client Retention Rate" 
          value={`${metrics.retentionRate}%`} 
          change={-2} 
          changeType="decrease" 
        />
        <MetricCard 
          title="Total Commission" 
          value={metrics.totalCommission} 
          change={5} 
          changeType="increase" 
          isCurrency={true} 
        />
      </div>

      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-5 pb-3">Sales Performance</h2>
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6 bg-white">
            <p className="text-[#101418] text-sm font-medium leading-normal">Total Sales This Month</p>
            <p className="text-[#101418] text-3xl font-bold leading-tight tracking-[-0.015em]">{formatNaira(metrics.totalSales)}</p>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6 bg-white">
            <p className="text-[#101418] text-sm font-medium leading-normal">Active Clients</p>
            <p className="text-[#101418] text-3xl font-bold leading-tight tracking-[-0.015em]">{metrics.activeClients}</p>
        </div>
      </div>
      
      <div className="w-full rounded-xl border border-[#d4dbe2] p-6 bg-white mb-6">
        <h3 className="text-[#101418] text-lg font-semibold mb-4">Monthly Sales Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={salesPerformanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#666" />
            <YAxis stroke="#666" />
            <Tooltip 
              formatter={(value, name) => [
                name === 'sales' ? formatNaira(Number(value)) : value,
                name === 'sales' ? 'Sales' : 'Policies Sold'
              ]}
              labelStyle={{ color: '#101418' }}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #d4dbe2',
                borderRadius: '8px'
              }}
            />
            <Bar 
              dataKey="sales" 
              fill="#3f7fbf" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex justify-between items-center pt-8 pb-3">
        <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em]">Client Portfolio</h2>
        
        {/* Pay for Selected Button */}
        {selectedPoliciesData.selectedCount > 0 && (
          <button
            className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              bulkPaymentLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } text-white`}
            onClick={handleBulkPayment}
            disabled={bulkPaymentLoading}
          >
            <span>{bulkPaymentLoading ? 'Processing...' : 'Pay for Selected'}</span>
            {!bulkPaymentLoading && (
              <span className="bg-blue-500 px-2 py-1 rounded text-sm">
                {selectedPoliciesData.selectedCount} • {formatNaira(selectedPoliciesData.selectedTotal)}
              </span>
            )}
          </button>
        )}
      </div>
      
      <div className="w-full overflow-hidden rounded-xl border border-[#d4dbe2] bg-white">
        <DataTable columns={portfolioColumns} data={clientPortfolio} />
      </div>
    </>
  );
};

export default BrokerDashboard; 