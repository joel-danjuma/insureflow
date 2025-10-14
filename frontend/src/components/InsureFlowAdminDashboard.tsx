'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/services/api';
import PaymentTestingPanel from '@/components/PaymentTestingPanel';

interface TransactionLog {
  id: number;
  transaction_reference: string;
  virtual_account_number: string;
  user_name: string;
  transaction_type: string;
  principal_amount: number;
  settled_amount: number;
  insureflow_commission: number;
  habari_commission: number;
  transaction_date: string;
  status: string;
}

interface CommissionAnalytics {
  total_revenue_generated: number;
  monthly_revenue: number;
  daily_revenue: number;
  revenue_growth_rate: number;
  avg_commission_per_transaction: number;
}

interface PlatformHealth {
  total_active_users: number;
  total_virtual_accounts: number;
  active_virtual_accounts: number;
  webhook_success_rate: number;
  failed_transactions_today: number;
  pending_settlements: number;
  system_uptime: string;
  api_response_time: number;
}

const InsureFlowAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showPaymentTesting, setShowPaymentTesting] = useState(false);

  // Fetch transaction logs
  const { data: transactionLogs, isLoading: logsLoading } = useQuery({
    queryKey: ['insureflow-transaction-logs'],
    queryFn: async () => {
      const response = await api.get('/admin/insureflow/transaction-logs');
      return response.data;
    },
    retry: 1,
  });

  // Fetch commission analytics
  const { data: commissionAnalytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['insureflow-commission-analytics'],
    queryFn: async () => {
      const response = await api.get('/admin/insureflow/commission-analytics');
      return response.data;
    },
    retry: 1,
  });

  // Fetch platform health
  const { data: platformHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['insureflow-platform-health'],
    queryFn: async () => {
      const response = await api.get('/admin/insureflow/platform-health');
      return response.data;
    },
    retry: 1,
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-NG');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">InsureFlow Admin Dashboard</h1>
        <p className="text-purple-100">Internal platform administration and monitoring</p>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'transactions', label: 'Transaction Logs' },
              { id: 'testing', label: 'Payment Testing' },
              { id: 'commissions', label: 'Commission Analytics' },
              { id: 'platform', label: 'Platform Health' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Total Revenue</h3>
                <p className="text-3xl font-bold">
                  {commissionAnalytics ? formatCurrency(commissionAnalytics.total_revenue_generated) : '₦0'}
                </p>
                <p className="text-green-100 text-sm mt-2">
                  {commissionAnalytics ? `${commissionAnalytics.revenue_growth_rate.toFixed(1)}% growth` : 'Loading...'}
                </p>
              </div>

              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Active Users</h3>
                <p className="text-3xl font-bold">
                  {platformHealth ? platformHealth.total_active_users : '0'}
                </p>
                <p className="text-blue-100 text-sm mt-2">Total registered users</p>
              </div>

              <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Virtual Accounts</h3>
                <p className="text-3xl font-bold">
                  {platformHealth ? platformHealth.total_virtual_accounts : '0'}
                </p>
                <p className="text-purple-100 text-sm mt-2">Total virtual accounts</p>
              </div>

              <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">System Uptime</h3>
                <p className="text-3xl font-bold">
                  {platformHealth ? platformHealth.system_uptime : '99.9%'}
                </p>
                <p className="text-orange-100 text-sm mt-2">Platform availability</p>
              </div>
            </div>
          )}

          {/* Transaction Logs Tab */}
          {activeTab === 'transactions' && (
            <div>
              <h3 className="text-xl font-semibold mb-4">Recent Transaction Logs</h3>
              {logsLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p>Loading transaction logs...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Reference
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          InsureFlow Commission
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {transactionLogs?.slice(0, 10).map((log: TransactionLog) => (
                        <tr key={log.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {log.transaction_reference}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.user_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(log.principal_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                            {formatCurrency(log.insureflow_commission)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              log.status === 'completed' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {log.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(log.transaction_date)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Commission Analytics Tab */}
          {activeTab === 'commissions' && (
            <div className="space-y-6">
              <h3 className="text-xl font-semibold mb-4">Commission Analytics</h3>
              {analyticsLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p>Loading commission analytics...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Total Revenue</h4>
                    <p className="text-3xl font-bold text-green-600">
                      {formatCurrency(commissionAnalytics?.total_revenue_generated || 0)}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Monthly Revenue</h4>
                    <p className="text-3xl font-bold text-blue-600">
                      {formatCurrency(commissionAnalytics?.monthly_revenue || 0)}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Growth Rate</h4>
                    <p className="text-3xl font-bold text-purple-600">
                      {commissionAnalytics ? `${commissionAnalytics.revenue_growth_rate.toFixed(1)}%` : '0%'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Platform Health Tab */}
          {activeTab === 'platform' && (
            <div className="space-y-6">
              <h3 className="text-xl font-semibold mb-4">Platform Health Metrics</h3>
              {healthLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p>Loading platform health...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">System Uptime</h4>
                    <p className="text-3xl font-bold text-green-600">
                      {platformHealth?.system_uptime || '99.9%'}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">API Response Time</h4>
                    <p className="text-3xl font-bold text-blue-600">
                      {platformHealth ? `${platformHealth.api_response_time}ms` : '0ms'}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Webhook Success Rate</h4>
                    <p className="text-3xl font-bold text-purple-600">
                      {platformHealth ? `${platformHealth.webhook_success_rate}%` : '0%'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Payment Testing Tab */}
          {activeTab === 'testing' && (
            <div className="p-6">
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Payment Flow Testing</h3>
                <p className="text-gray-600">
                  Comprehensive testing interface for stakeholder demonstrations and system validation.
                </p>
              </div>
              <PaymentTestingPanel />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InsureFlowAdminDashboard; 