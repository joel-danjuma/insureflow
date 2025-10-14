'use client';

import React, { useState, useMemo } from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { formatNaira } from '@/utils/currency';
import { useBrokerProfile, usePolicies, usePremiums } from '@/hooks/useQuery';
import { Policy, Premium } from '@/types/user';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { paymentService, premiumService, notificationService } from '@/services/api';
import useReminderStore from '@/store/reminderStore';
import useAuthStore from '@/store/authStore';
import usePolicyStore from '@/store/policyStore';
import usePaymentStore from '@/store/paymentStore';
import PaymentModal from '@/components/PaymentModal';
import PaymentTestingPanel from '@/components/PaymentTestingPanel';

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
  const { user } = useAuthStore();
  const getRemindersForBroker = useReminderStore((state) => state.getRemindersForBroker);
  const brokerReminders = user ? getRemindersForBroker(user.id) : [];
  const [dismissedReminders, setDismissedReminders] = useState<Set<string>>(new Set());

  // Early return for loading states to prevent render errors
  if (brokerLoading || policiesLoading || premiumsLoading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="flex flex-wrap justify-between gap-3 pb-4">
          <div className="flex min-w-72 flex-col gap-3">
            <div className="h-8 bg-gray-700 rounded w-64 animate-pulse"></div>
            <div className="h-4 bg-gray-700 rounded w-96 animate-pulse"></div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <MetricCard key={i} title="" value="" isLoading={true} />
          ))}
        </div>
        
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="h-6 bg-gray-700 rounded w-48 mb-4 animate-pulse"></div>
            <div className="h-64 bg-gray-700 rounded animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  // Early return for critical errors
  if (brokerError && policiesError && premiumsError) {
    return (
      <div className="min-h-screen bg-gray-900 p-6 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Unable to Load Dashboard</h2>
          <p className="text-gray-400 mb-4">There was an error loading your dashboard data.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // State for selected policies
  const [selectedPolicies, setSelectedPolicies] = useState<Set<string>>(new Set());
  const [paymentLoading, setPaymentLoading] = useState<Set<string>>(new Set());
  const [bulkPaymentLoading, setBulkPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState<string | null>(null);
  const addPayment = usePaymentStore((state) => state.addPayment);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentSuccessState, setPaymentSuccessState] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  
  // Payment testing panel state
  const [showPaymentTesting, setShowPaymentTesting] = useState(false);

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
    // Ensure policies is an array and has valid data
    const validPolicies = Array.isArray(policies) ? policies : [];
    
    // Calculate total premiums with null checks
    const totalPremiums = validPolicies.reduce((sum, policy) => {
      const premiumAmount = typeof policy?.premium_amount === 'number' ? policy.premium_amount : 0;
      return sum + premiumAmount;
    }, 0);
    
    // Calculate commission (15% of total premiums)
    const totalCommission = totalPremiums * 0.15;
    
    // Calculate active clients with null checks
    const activeClients = new Set(
      validPolicies
        .filter(p => p?.customer_id != null)
        .map(p => p.customer_id)
    ).size;
    
    // Calculate retention rate
    const retentionRate = validPolicies.length > 0 ? Math.round((activeClients / validPolicies.length) * 100) : 0;
    
    return {
      totalPremiums: isNaN(totalPremiums) ? 0 : totalPremiums,
      totalCommission: isNaN(totalCommission) ? 0 : totalCommission,
      retentionRate: isNaN(retentionRate) ? 0 : retentionRate,
      activeClients: isNaN(activeClients) ? 0 : activeClients,
    };
  };

  // Transform policies into client portfolio with payment status
  const transformToClientPortfolio = React.useCallback((policies: Policy[]): ClientPortfolioItem[] => {
    // Ensure policies is an array
    const validPolicies = Array.isArray(policies) ? policies : [];
    
    return validPolicies.map(policy => {
      // Handle potential undefined dates
      const endDate = policy?.end_date ? new Date(policy.end_date) : new Date();
      const nextPaymentDate = isNaN(endDate.getTime()) ? new Date() : endDate;
      const today = new Date();
      const daysDiff = Math.ceil((nextPaymentDate.getTime() - today.getTime()) / (1000 * 3600 * 24));
      
      let paymentStatus: 'Paid' | 'Pending' | 'Overdue' = 'Pending';
      if (daysDiff < 0) {
        paymentStatus = 'Overdue';
      } else if (policy?.status === 'active' && daysDiff > 30) {
        paymentStatus = 'Paid';
      }

      // Find the corresponding premium for this policy
      const premium = premiums?.find(p => p?.policy_id === policy?.id);
      
      // Ensure premium amount is a valid number
      const premiumAmount = typeof policy?.premium_amount === 'number' ? policy.premium_amount : 0;

      return {
        id: policy?.id?.toString() || 'unknown',
        policyId: policy?.id || 0,
        premiumId: premium?.id || null,
        clientName: policy?.customer?.full_name || 'Unknown Client',
        policyType: policy?.policy_type || 'Unknown',
        policyStatus: policy?.status === 'active' ? 'Active' : 'Pending',
        paymentStatus,
        premiumAmount: formatNaira(premiumAmount),
        premiumAmountRaw: premiumAmount,
        nextPaymentDate: nextPaymentDate.toLocaleDateString('en-GB'),
      };
    });
  }, [premiums]);

  const localPolicies = usePolicyStore((state) => state.getPolicies());

  // Merge backend and local policies
  const allPolicies = useMemo(() => {
    const backendPolicies = Array.isArray(policies) ? policies : [];
    const validLocalPolicies = Array.isArray(localPolicies) ? localPolicies : [];
    
    const localPoliciesData = validLocalPolicies.map(localPolicy => ({
      id: parseInt(localPolicy?.id?.split('-')[0]) || Math.floor(Math.random() * 10000),
      policy_number: localPolicy?.policy_number || `LOCAL-${localPolicy?.id || 'unknown'}`,
      policy_type: localPolicy?.policy_type || 'unknown',
      customer_id: Math.floor(Math.random() * 1000),
      broker_id: Math.floor(Math.random() * 100),
      coverage_amount: typeof localPolicy?.coverage_amount === 'number' ? localPolicy.coverage_amount : 0,
      premium_amount: typeof localPolicy?.premium_amount === 'number' ? localPolicy.premium_amount : 0,
      start_date: localPolicy?.start_date || new Date().toISOString(),
      end_date: localPolicy?.due_date || new Date().toISOString(),
      status: 'active',
      customer: {
        full_name: localPolicy?.contact_person || 'Unknown Client',
        email: localPolicy?.contact_email || 'unknown@example.com',
      },
      broker: {
        name: 'Local Broker',
      },
    }));
    return [...backendPolicies, ...localPoliciesData];
  }, [policies, localPolicies]);

  const clientPortfolio = useMemo(() => 
    transformToClientPortfolio(allPolicies), 
    [allPolicies, transformToClientPortfolio]
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

  // Handle single premium payment
  const handleSinglePayment = async (premiumId: number, policyId: string) => {
    const policy = clientPortfolio.find(item => item.id === policyId);
    if (!policy) return;

    setSelectedPolicies(new Set([policyId]));
    setShowPaymentModal(true);
  };

  // Handle bulk payment
  const handleBulkPayment = async () => {
    if (selectedPolicies.size === 0) {
      setPaymentError('No policies selected for payment');
      return;
    }
    setShowPaymentModal(true);
  };

  // Handle payment completion
  const handleCompletePayment = async (paymentMethod: 'bank_transfer' | 'ussd') => {
    // Set loading state for the modal
    setPaymentError(null);
    setPaymentSuccess(null);
    setPaymentSuccessState(false);

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Get selected policies data
      const selectedPoliciesData = clientPortfolio.filter(item => selectedPolicies.has(item.id));
      
      // Create payment record
      const paymentRecord = {
        id: `payment-${Date.now()}`,
        brokerId: user?.id || 0,
        brokerName: brokerProfile?.name || 'Unknown Broker',
        totalAmount: selectedPoliciesData.reduce((sum, item) => sum + item.premiumAmountRaw, 0),
        policies: selectedPoliciesData.map(item => ({
          policyId: item.policyId,
          policyNumber: item.clientName.split(' ')[0] + '-POL-' + item.policyId,
          customerName: item.clientName,
          amount: item.premiumAmountRaw,
        })),
        paymentMethod,
        status: 'completed' as const,
        completedAt: new Date().toISOString(),
      };

      // Add to payment store
      addPayment(paymentRecord);

      // Show success state in modal
      setPaymentSuccessState(true);

      setTimeout(() => {
        setPaymentSuccess(`Payment completed successfully! ${selectedPoliciesData.length} policies paid via ${paymentMethod === 'bank_transfer' ? 'Bank Transfer' : 'USSD'}.`);
        setSelectedPolicies(new Set());
        setShowPaymentModal(false);
        setPaymentSuccessState(false);
      }, 2000);
    } catch (error) {
      setPaymentError('Payment failed. Please try again.');
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
      header: () => (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={isAllSelected}
            ref={(el) => {
              if (el) el.indeterminate = isPartiallySelected;
            }}
            onChange={(e) => handleSelectAll(e.target.checked)}
            className="w-4 h-4 text-orange-500 bg-gray-700 border-gray-600 rounded focus:ring-orange-500 focus:ring-2"
          />
        </div>
      ),
      cell: ({ row }) => (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selectedPolicies.has(row.original.id)}
            onChange={(e) => handleRowSelection(row.original.id, e.target.checked)}
            className="w-4 h-4 text-orange-500 bg-gray-700 border-gray-600 rounded focus:ring-orange-500 focus:ring-2"
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
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${isActive ? 'bg-green-900/30 text-green-400 border border-green-500/30' : 'bg-yellow-900/30 text-yellow-400 border border-yellow-500/30'}`}>
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
          'Paid': 'bg-green-900/30 text-green-400 border-green-500/30',
          'Pending': 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30',
          'Overdue': 'bg-red-900/30 text-red-400 border-red-500/30'
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
            <span className="text-green-400 text-sm font-medium">Paid</span>
          );
        }
        
        return (
          <button
            onClick={() => handleSinglePayment(item.premiumId!, item.id)}
            disabled={!item.premiumId || isLoading}
            className={`px-3 py-1 text-sm font-medium rounded transition-colors ${
              !item.premiumId || isLoading
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-orange-500 text-white hover:bg-orange-600'
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
            <div className="h-8 bg-gray-700 rounded w-48 animate-pulse"></div>
            <div className="h-4 bg-gray-700 rounded w-96 animate-pulse"></div>
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
          <div className="h-6 bg-gray-700 rounded w-48 animate-pulse"></div>
          <div className="flex flex-wrap gap-4">
            <div className="h-32 bg-gray-800 rounded-xl border border-gray-700 animate-pulse flex-1 min-w-72"></div>
            <div className="h-32 bg-gray-800 rounded-xl border border-gray-700 animate-pulse flex-1 min-w-72"></div>
          </div>
        </div>
        
        {/* Table skeleton */}
        <div className="space-y-6">
          <div className="h-6 bg-gray-700 rounded w-48 animate-pulse"></div>
          <div className="h-64 bg-gray-800 rounded-xl border border-gray-700 animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (brokerError || policiesError || premiumsError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center p-8 border border-red-500/30 rounded-lg bg-red-900/20">
          <div className="text-red-400 text-xl font-semibold mb-2">Error Loading Dashboard</div>
          <p className="text-red-300 mb-4">
            Error: An unexpected error occurred while fetching broker profile.
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const metrics = useMemo(() => calculateBrokerMetrics(allPolicies, premiums || []), [allPolicies, premiums]);

  // Mock chart data for premium performance
  const premiumPerformanceData = [
    { month: 'Jan', premiums: 45000000, policies: 12 },
    { month: 'Feb', premiums: 52000000, policies: 14 },
    { month: 'Mar', premiums: 48000000, policies: 13 },
    { month: 'Apr', premiums: 61000000, policies: 16 },
    { month: 'May', premiums: 55000000, policies: 15 },
    { month: 'Jun', premiums: 70000000, policies: 18 },
  ];

  return (
    <>
      {/* Dummy Payment Reminders */}
      {brokerReminders.filter(r => !dismissedReminders.has(r.id)).map(reminder => (
        <div key={reminder.id} className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 mb-4 flex justify-between items-center">
          <div>
            <span className="text-yellow-400 font-bold mr-2">Payment Reminder:</span>
            <span className="text-white">Policy <b>{reminder.policyNumber}</b> for <b>{reminder.customerName}</b> is overdue by <b>{reminder.daysOverdue} days</b>. Premium: <b>{reminder.premiumAmount}</b></span>
          </div>
          <button onClick={() => setDismissedReminders(prev => new Set(prev).add(reminder.id))} className="ml-4 px-3 py-1 rounded bg-yellow-700 text-white hover:bg-yellow-800">Dismiss</button>
        </div>
      ))}
      <div className="flex flex-wrap justify-between gap-3 pb-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-white tracking-light text-[32px] font-bold leading-tight">
            {brokerProfile?.name || 'Broker'} Dashboard
          </p>
          <p className="text-gray-400 text-sm font-normal leading-normal">Overview of your performance and client portfolio</p>
        </div>
      </div>

      {/* Payment status messages */}
      {paymentError && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="text-red-400 text-sm">
              <strong>Error:</strong> {paymentError}
            </div>
          </div>
        </div>
      )}

      {paymentSuccess && (
        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="text-green-400 text-sm">
              <strong>Success:</strong> {paymentSuccess}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <MetricCard 
          title="Total Premiums" 
          value={metrics.totalPremiums} 
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

      <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em] pt-5 pb-3">Premium Performance</h2>
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-gray-700 p-6 bg-gray-800">
            <p className="text-gray-400 text-sm font-medium leading-normal">Total Premiums This Month</p>
            <p className="text-white text-3xl font-bold leading-tight tracking-[-0.015em]">{formatNaira(metrics.totalPremiums)}</p>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-gray-700 p-6 bg-gray-800">
            <p className="text-gray-400 text-sm font-medium leading-normal">Active Clients</p>
            <p className="text-white text-3xl font-bold leading-tight tracking-[-0.015em]">{metrics.activeClients}</p>
        </div>
      </div>
      
      <div className="w-full rounded-xl border border-gray-700 p-6 bg-gray-800 mb-6">
        <h3 className="text-white text-lg font-semibold mb-4">Monthly Premium Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={premiumPerformanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              formatter={(value, name) => [
                name === 'premiums' ? formatNaira(Number(value)) : value,
                name === 'premiums' ? 'Premiums' : 'Policies Sold'
              ]}
              labelStyle={{ color: '#ffffff' }}
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#ffffff'
              }}
            />
            <Bar 
              dataKey="premiums" 
              fill="#F97316" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex justify-between items-center pt-8 pb-3">
        <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">Client Portfolio</h2>
        
        {/* Pay for Selected Button */}
        {selectedPoliciesData.selectedCount > 0 && (
          <button
            className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              bulkPaymentLoading
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-orange-500 hover:bg-orange-600'
            } text-white`}
            onClick={handleBulkPayment}
            disabled={bulkPaymentLoading}
          >
            <span>{bulkPaymentLoading ? 'Processing...' : 'Pay for Selected'}</span>
            {!bulkPaymentLoading && (
              <span className="bg-orange-600 px-2 py-1 rounded text-sm">
                {selectedPoliciesData.selectedCount} • {formatNaira(selectedPoliciesData.selectedTotal)}
              </span>
            )}
          </button>
        )}
      </div>
      
      <div className="w-full overflow-hidden rounded-xl border border-gray-700 bg-gray-800">
        <DataTable columns={portfolioColumns} data={clientPortfolio} />
      </div>

      {/* Payment Flow Testing Section - For Stakeholder Demos */}
      <div className="flex justify-between items-center pt-8 pb-3">
        <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">
          Payment Flow Testing
        </h2>
        <div className="flex gap-3">
          <button
            onClick={() => setShowPaymentTesting(!showPaymentTesting)}
            className="px-4 py-2 border border-blue-500 text-blue-400 rounded-lg font-medium hover:bg-blue-500/10 transition-colors"
          >
            {showPaymentTesting ? 'Hide Testing Panel' : 'Show Testing Panel'}
          </button>
          <div className="text-gray-400 text-sm">
            For stakeholder demonstrations
          </div>
        </div>
      </div>

      {showPaymentTesting && (
        <div className="mb-8">
          <PaymentTestingPanel />
        </div>
      )}

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          setPaymentSuccessState(false);
        }}
        onCompletePayment={handleCompletePayment}
        selectedPolicies={clientPortfolio.filter(item => selectedPolicies.has(item.id)).map(item => ({
          id: item.id,
          policyNumber: item.clientName.split(' ')[0] + '-POL-' + item.policyId,
          customerName: item.clientName,
          premiumAmount: item.premiumAmount,
          premiumAmountRaw: item.premiumAmountRaw,
        }))}
        totalAmount={selectedPoliciesData.selectedTotal}
        isLoading={false}
        isSuccess={paymentSuccessState}
      />
    </>
  );
};

export default BrokerDashboard; 