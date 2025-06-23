'use client';

import React, { useState, useMemo } from 'react';
import MetricCard from '@/components/MetricCard';
import { DataTable } from '@/components/DataTable';
import { ColumnDef } from '@tanstack/react-table';
import { formatNaira } from '@/utils/currency';
import { useDashboardData, usePolicies, usePremiums } from '@/hooks/useQuery';
import { RecentPolicy, Policy, Premium } from '@/types/user';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { reminderService } from '@/services/api';

// For displaying broker performance (calculated from policies data)
type BrokerPerformance = {
  name: string;
  policiesSold: number;
  commission: string;
  satisfaction: number;
};

// For displaying outstanding policies that need reminders
type OutstandingPolicy = {
  id: string;
  policyId: number;
  brokerId: number;
  policyNumber: string;
  customerName: string;
  brokerName: string;
  premiumAmount: string;
  premiumAmountRaw: number;
  daysOverdue: number;
  lastPaymentDate: string;
};

const brokerColumns: ColumnDef<BrokerPerformance>[] = [
    { accessorKey: 'name', header: 'Broker Name' },
    { accessorKey: 'policiesSold', header: 'Policies Sold' },
    { accessorKey: 'commission', header: 'Commission Earned' },
    { 
      accessorKey: 'satisfaction', 
      header: 'Client Satisfaction',
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
            <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2] h-1.5">
              <div className="h-full rounded-full bg-[#3f7fbf]" style={{ width: `${row.original.satisfaction}%` }}></div>
            </div>
            <p className="text-[#101418] text-sm font-medium leading-normal">{row.original.satisfaction}%</p>
        </div>
      )
    },
];

const recentPoliciesColumns: ColumnDef<RecentPolicy>[] = [
    { accessorKey: 'policy_number', header: 'Policy Number' },
    { accessorKey: 'customer_name', header: 'Customer Name' },
    { accessorKey: 'broker', header: 'Broker' },
];

const InsuranceFirmDashboard = () => {
  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } = useDashboardData();
  const { data: policies, isLoading: policiesLoading, error: policiesError } = usePolicies();
  const { data: premiums, isLoading: premiumsLoading, error: premiumsError } = usePremiums();

  // State for payment reminders
  const [selectedPolicies, setSelectedPolicies] = useState<Set<string>>(new Set());
  const [reminderLoading, setReminderLoading] = useState(false);
  const [reminderError, setReminderError] = useState<string | null>(null);
  const [reminderSuccess, setReminderSuccess] = useState<string | null>(null);
  const [showReminderSection, setShowReminderSection] = useState(false);

  // Clear messages after 5 seconds
  React.useEffect(() => {
    if (reminderError || reminderSuccess) {
      const timer = setTimeout(() => {
        setReminderError(null);
        setReminderSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [reminderError, reminderSuccess]);

  // Calculate broker performance from policies data
  const calculateBrokerPerformance = (policies: Policy[]): BrokerPerformance[] => {
    const brokerMap = new Map<string, { policies: number; totalCommission: number }>();
    
    policies.forEach(policy => {
      const brokerName = policy.broker?.name || 'Unassigned';
      const commission = policy.premium_amount * 0.15; // 15% commission rate
      
      if (brokerMap.has(brokerName)) {
        const existing = brokerMap.get(brokerName)!;
        existing.policies += 1;
        existing.totalCommission += commission;
      } else {
        brokerMap.set(brokerName, { policies: 1, totalCommission: commission });
      }
    });

    return Array.from(brokerMap.entries()).map(([name, data]) => ({
      name,
      policiesSold: data.policies,
      commission: formatNaira(data.totalCommission),
      satisfaction: Math.floor(Math.random() * 20) + 80, // Mock satisfaction score for now
    }));
  };

  // Calculate claims data from premiums
  const calculateClaimsData = (premiums: Premium[]) => {
    const totalClaims = premiums.filter(p => p.payment_status === 'paid').length;
    const totalPayout = premiums
      .filter(p => p.payment_status === 'paid')
      .reduce((sum, p) => sum + p.amount, 0);
    
    return { totalClaims, totalPayout };
  };

  // Calculate outstanding policies that need reminders
  const calculateOutstandingPolicies = (policies: Policy[], premiums: Premium[]): OutstandingPolicy[] => {
    const outstandingPolicies: OutstandingPolicy[] = [];
    
    policies.forEach(policy => {
      // Find unpaid premiums for this policy
      const unpaidPremiums = premiums.filter(p => 
        p.policy_id === policy.id && p.payment_status !== 'paid'
      );
      
      if (unpaidPremiums.length > 0) {
        const oldestPremium = unpaidPremiums[0]; // Assuming first is oldest
        const dueDate = new Date(policy.end_date);
        const today = new Date();
        const daysOverdue = Math.max(0, Math.ceil((today.getTime() - dueDate.getTime()) / (1000 * 3600 * 24)));
        
        // Only include if overdue or due soon
        if (daysOverdue > 0 || daysOverdue >= -7) {
          outstandingPolicies.push({
            id: policy.id.toString(),
            policyId: policy.id,
            brokerId: (policy.broker as any)?.id || policy.id, // Fallback to policy id if broker id doesn't exist
            policyNumber: policy.policy_number,
            customerName: policy.customer?.full_name || 'Unknown Customer',
            brokerName: policy.broker?.name || 'Unassigned',
            premiumAmount: formatNaira(policy.premium_amount),
            premiumAmountRaw: policy.premium_amount,
            daysOverdue: Math.abs(daysOverdue),
            lastPaymentDate: new Date(policy.start_date).toLocaleDateString('en-GB'),
          });
        }
      }
    });
    
    return outstandingPolicies.sort((a, b) => b.daysOverdue - a.daysOverdue);
  };

  const outstandingPolicies = useMemo(() => 
    calculateOutstandingPolicies(policies || [], premiums || []), 
    [policies, premiums]
  );

  // Handle individual row selection for reminders
  const handlePolicySelection = (policyId: string, isSelected: boolean) => {
    const newSelected = new Set(selectedPolicies);
    if (isSelected) {
      newSelected.add(policyId);
    } else {
      newSelected.delete(policyId);
    }
    setSelectedPolicies(newSelected);
  };

  // Handle select all for reminders
  const handleSelectAllPolicies = (isSelected: boolean) => {
    if (isSelected) {
      setSelectedPolicies(new Set(outstandingPolicies.map(policy => policy.id)));
    } else {
      setSelectedPolicies(new Set());
    }
  };

  // Handle sending reminders
  const handleSendReminders = async () => {
    const selectedPolicyIds = Array.from(selectedPolicies).map(id => parseInt(id));
    const selectedBrokerIds = outstandingPolicies
      .filter(policy => selectedPolicies.has(policy.id))
      .map(policy => policy.brokerId)
      .filter((id, index, self) => self.indexOf(id) === index); // Remove duplicates
    
    if (selectedPolicyIds.length === 0) {
      setReminderError('No policies selected for reminders');
      return;
    }

    setReminderLoading(true);
    setReminderError(null);
    setReminderSuccess(null);

    try {
      await reminderService.sendReminders({
        policy_ids: selectedPolicyIds,
        broker_ids: selectedBrokerIds,
      });
      
      setReminderSuccess(
        `Reminders sent successfully for ${selectedPolicyIds.length} policies to ${selectedBrokerIds.length} brokers.`
      );
      
      // Clear selection after successful sending
      setSelectedPolicies(new Set());
    } catch (error) {
      setReminderError(error instanceof Error ? error.message : 'Failed to send reminders');
    } finally {
      setReminderLoading(false);
    }
  };

  // Check if all policies are selected
  const isAllPoliciesSelected = outstandingPolicies.length > 0 && selectedPolicies.size === outstandingPolicies.length;
  const isPartiallySelected = selectedPolicies.size > 0 && selectedPolicies.size < outstandingPolicies.length;

  const outstandingPoliciesColumns: ColumnDef<OutstandingPolicy>[] = [
    {
      id: 'select',
      header: ({ table }) => (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={isAllPoliciesSelected}
            ref={(el) => {
              if (el) el.indeterminate = isPartiallySelected;
            }}
            onChange={(e) => handleSelectAllPolicies(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
        </div>
      ),
      cell: ({ row }) => (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selectedPolicies.has(row.original.id)}
            onChange={(e) => handlePolicySelection(row.original.id, e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
        </div>
      ),
      enableSorting: false,
    },
    { accessorKey: 'policyNumber', header: 'Policy Number' },
    { accessorKey: 'customerName', header: 'Customer Name' },
    { accessorKey: 'brokerName', header: 'Broker' },
    { accessorKey: 'premiumAmount', header: 'Premium Amount' },
    { 
      accessorKey: 'daysOverdue', 
      header: 'Days Overdue',
      cell: ({ row }) => {
        const days = row.original.daysOverdue;
        return (
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            days > 30 ? 'bg-red-100 text-red-800 border border-red-200' :
            days > 7 ? 'bg-orange-100 text-orange-800 border border-orange-200' :
            'bg-yellow-100 text-yellow-800 border border-yellow-200'
          }`}>
            {days} days
          </span>
        );
      }
    },
    { accessorKey: 'lastPaymentDate', header: 'Last Payment' },
  ];

  if (dashboardLoading || policiesLoading || premiumsLoading) {
    return (
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="flex flex-wrap justify-between gap-3 py-4">
          <div className="flex min-w-72 flex-col gap-3">
            <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
          </div>
        </div>
        
        {/* Metric cards skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <MetricCard key={i} title="" value="" isLoading={true} />
          ))}
        </div>
        
        {/* Tables skeleton */}
        <div className="space-y-6">
          <div className="h-6 bg-gray-200 rounded w-48 animate-pulse"></div>
          <div className="h-64 bg-gray-100 rounded-xl border border-gray-200 animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (dashboardError || policiesError || premiumsError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center p-8 border border-red-200 rounded-lg bg-red-50">
          <div className="text-red-600 text-xl font-semibold mb-2">Error Loading Dashboard</div>
          <p className="text-red-500 mb-4">
            {(dashboardError || policiesError || premiumsError)?.toString()}
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

  const brokerPerformance = policies ? calculateBrokerPerformance(policies) : [];
  const claimsData = premiums ? calculateClaimsData(premiums) : { totalClaims: 0, totalPayout: 0 };

  // Mock chart data for claims trends
  const claimsTrendData = [
    { month: 'Jan', claims: 45, payout: 67500000 },
    { month: 'Feb', claims: 52, payout: 78000000 },
    { month: 'Mar', claims: 48, payout: 72000000 },
    { month: 'Apr', claims: 61, payout: 91500000 },
    { month: 'May', claims: 55, payout: 82500000 },
    { month: 'Jun', claims: 70, payout: 105000000 },
  ];

  return (
    <>
      <div className="flex flex-wrap justify-between gap-3 py-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-text-primary tracking-light text-[28px] font-bold leading-tight">Dashboard</p>
          <p className="text-text-secondary text-sm font-normal leading-normal">Overview of key metrics and performance indicators</p>
        </div>
      </div>

      {/* Payment reminder status messages */}
      {reminderError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="text-red-600 text-sm">
              <strong>Error:</strong> {reminderError}
            </div>
          </div>
        </div>
      )}

      {reminderSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="text-green-600 text-sm">
              <strong>Success:</strong> {reminderSuccess}
            </div>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="New Policies" 
          value={dashboardData?.kpis.new_policies_this_month || 0} 
          change={15} 
          changeType="increase" 
        />
        <MetricCard 
          title="Outstanding Premiums" 
          value={dashboardData?.kpis.outstanding_premiums_total || 0} 
          change={-5} 
          changeType="decrease" 
          isCurrency={true} 
        />
        <MetricCard 
          title="Total Brokers" 
          value={dashboardData?.kpis.broker_count || 0} 
          change={10} 
          changeType="increase" 
        />
        <MetricCard 
          title="Claims Processed" 
          value={claimsData.totalClaims} 
          change={8} 
          changeType="increase" 
        />
      </div>

      {/* Payment Reminder System Section */}
      <div className="flex justify-between items-center pt-8 pb-3">
        <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em]">
          Payment Reminders
        </h2>
        <div className="flex gap-3">
          <button
            onClick={() => setShowReminderSection(!showReminderSection)}
            className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
          >
            {showReminderSection ? 'Hide Reminders' : `View Outstanding (${outstandingPolicies.length})`}
          </button>
          {selectedPolicies.size > 0 && (
            <button
              onClick={handleSendReminders}
              disabled={reminderLoading}
              className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                reminderLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-orange-600 hover:bg-orange-700'
              } text-white`}
            >
              {reminderLoading ? 'Sending...' : `Send Reminders (${selectedPolicies.size})`}
            </button>
          )}
        </div>
      </div>

      {showReminderSection && (
        <div className="w-full overflow-hidden rounded-xl border border-[#d4dbe2] bg-white mb-6">
          {outstandingPolicies.length > 0 ? (
            <DataTable columns={outstandingPoliciesColumns} data={outstandingPolicies} />
          ) : (
            <div className="p-8 text-center">
              <div className="text-green-600 text-lg font-semibold mb-2">All Caught Up!</div>
              <p className="text-gray-500">No outstanding premiums requiring reminders at this time.</p>
            </div>
          )}
        </div>
      )}
      
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Recent Policies</h2>
      <div className="w-full overflow-hidden rounded-xl border border-[#d4dbe2] bg-white">
        <DataTable 
          columns={recentPoliciesColumns} 
          data={dashboardData?.recent_policies || []} 
        />
      </div>

      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Broker Performance</h2>
      <div className="w-full overflow-hidden rounded-xl border border-[#d4dbe2] bg-white">
        <DataTable columns={brokerColumns} data={brokerPerformance} />
      </div>

      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] pt-8 pb-3">Claims Data</h2>
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6 bg-white">
            <p className="text-[#101418] text-sm font-medium leading-normal">Total Claims Processed</p>
            <p className="text-[#101418] text-3xl font-bold leading-tight tracking-[-0.015em]">{claimsData.totalClaims}</p>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6 bg-white">
            <p className="text-[#101418] text-sm font-medium leading-normal">Total Claims Payout</p>
            <p className="text-[#101418] text-3xl font-bold leading-tight tracking-[-0.015em]">{formatNaira(claimsData.totalPayout)}</p>
        </div>
      </div>
      
      <div className="w-full rounded-xl border border-[#d4dbe2] p-6 bg-white">
        <h3 className="text-[#101418] text-lg font-semibold mb-4">Claims Trends (6 Months)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={claimsTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#666" />
            <YAxis stroke="#666" />
            <Tooltip 
              formatter={(value, name) => [
                name === 'payout' ? formatNaira(Number(value)) : value,
                name === 'payout' ? 'Payout' : 'Claims'
              ]}
              labelStyle={{ color: '#101418' }}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #d4dbe2',
                borderRadius: '8px'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="claims" 
              stroke="#3f7fbf" 
              fill="#3f7fbf" 
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default InsuranceFirmDashboard;