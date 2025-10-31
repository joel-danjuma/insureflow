'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';
import { supportService } from '@/services/api';

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

interface SupportTicket {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high';
  category: string;
  user_id: number;
  admin_response?: string;
  assigned_to?: number;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

const InsureFlowAdminDashboard = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('overview');
  const [ticketFilters, setTicketFilters] = useState<{ status?: string; priority?: string; category?: string }>({});
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [adminResponse, setAdminResponse] = useState('');
  const [updateStatus, setUpdateStatus] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

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

  // Fetch support tickets
  const { data: supportTickets = [], isLoading: ticketsLoading, refetch: refetchTickets } = useQuery({
    queryKey: ['admin-support-tickets', ticketFilters],
    queryFn: async () => {
      const data = await supportService.getAllTickets(
        ticketFilters.status,
        ticketFilters.priority,
        ticketFilters.category
      );
      return data;
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

  const getStatusColor = (status: string) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.open;
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800',
    };
    return colors[priority as keyof typeof colors] || colors.medium;
  };

  const handleTicketClick = (ticket: SupportTicket) => {
    setSelectedTicket(ticket);
    setShowTicketModal(true);
    setAdminResponse(ticket.admin_response || '');
    setUpdateStatus(ticket.status);
  };

  const handleUpdateTicket = async () => {
    if (!selectedTicket) return;
    
    setIsUpdating(true);
    try {
      const updateData: any = {};
      if (adminResponse && adminResponse.trim() !== selectedTicket.admin_response) {
        updateData.admin_response = adminResponse.trim();
      }
      if (updateStatus && updateStatus !== selectedTicket.status) {
        updateData.status = updateStatus;
      }
      
      if (Object.keys(updateData).length > 0) {
        await supportService.updateTicket(selectedTicket.id, updateData);
        queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] });
        refetchTickets();
        setShowTicketModal(false);
        setSelectedTicket(null);
        setAdminResponse('');
        setUpdateStatus('');
      }
    } catch (error: any) {
      console.error('Error updating ticket:', error);
      alert('Failed to update ticket: ' + (error.message || 'Unknown error'));
    } finally {
      setIsUpdating(false);
    }
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
              { id: 'commissions', label: 'Commission Analytics' },
              { id: 'platform', label: 'Platform Health' },
              { id: 'support-tickets', label: 'Support Tickets' },
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

          {/* Support Tickets Tab */}
          {activeTab === 'support-tickets' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold">Support Tickets</h3>
              </div>

              {/* Filters */}
              <div className="bg-gray-50 p-4 rounded-lg flex gap-4">
                <select
                  value={ticketFilters.status || ''}
                  onChange={(e) => setTicketFilters(prev => ({ ...prev, status: e.target.value || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>

                <select
                  value={ticketFilters.priority || ''}
                  onChange={(e) => setTicketFilters(prev => ({ ...prev, priority: e.target.value || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">All Priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>

                <select
                  value={ticketFilters.category || ''}
                  onChange={(e) => setTicketFilters(prev => ({ ...prev, category: e.target.value || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="">All Categories</option>
                  <option value="general">General</option>
                  <option value="policies">Policies</option>
                  <option value="payments">Payments</option>
                  <option value="commissions">Commissions</option>
                  <option value="technical">Technical</option>
                </select>
              </div>

              {ticketsLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p>Loading support tickets...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Title
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Category
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Priority
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Created
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {supportTickets.length === 0 ? (
                        <tr>
                          <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500">
                            No support tickets found
                          </td>
                        </tr>
                      ) : (
                        supportTickets.map((ticket: SupportTicket) => (
                          <tr key={ticket.id} className="hover:bg-gray-50 cursor-pointer">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              #{ticket.id}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {ticket.title}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {ticket.category}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(ticket.status)}`}>
                                {ticket.status.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(ticket.priority)}`}>
                                {ticket.priority}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(ticket.created_at)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <button
                                onClick={() => handleTicketClick(ticket)}
                                className="text-purple-600 hover:text-purple-900"
                              >
                                View/Update
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      {/* Ticket Detail/Update Modal */}
      {showTicketModal && selectedTicket && (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Ticket #{selectedTicket.id}</h3>
              <button
                onClick={() => {
                  setShowTicketModal(false);
                  setSelectedTicket(null);
                  setAdminResponse('');
                  setUpdateStatus('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <p className="text-gray-900 font-medium">{selectedTicket.title}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <p className="text-gray-900">{selectedTicket.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <p className="text-gray-900">{selectedTicket.category}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(selectedTicket.priority)}`}>
                    {selectedTicket.priority}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={updateStatus}
                  onChange={(e) => setUpdateStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Admin Response</label>
                <textarea
                  value={adminResponse}
                  onChange={(e) => setAdminResponse(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Add your response to this ticket..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => {
                    setShowTicketModal(false);
                    setSelectedTicket(null);
                    setAdminResponse('');
                    setUpdateStatus('');
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateTicket}
                  disabled={isUpdating}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                  {isUpdating ? 'Updating...' : 'Update Ticket'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InsureFlowAdminDashboard; 