'use client';

import React, { useState } from 'react';
import Layout from '@/components/Layout';
import withAuth from '@/hocs/withAuth';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';

interface Policy {
  id: number;
  policy_number: string;
  client_name: string;
  premium_amount: number;
  due_date: string;
  payment_status: 'paid' | 'pending' | 'overdue';
  last_reminder_sent?: string;
}

interface ReminderHistory {
  id: number;
  policy_number: string;
  client_name: string;
  sent_at: string;
  status: 'sent' | 'delivered' | 'failed';
  message: string;
}

const RemindersPage = () => {
  const queryClient = useQueryClient();
  const [selectedPolicies, setSelectedPolicies] = useState<number[]>([]);
  const [customMessage, setCustomMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Fetch policies that need reminders
  const { data: policies = [], isLoading: policiesLoading } = useQuery({
    queryKey: ['policies-for-reminders'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return [
        {
          id: 1,
          policy_number: 'POL-2024-001',
          client_name: 'John Doe',
          premium_amount: 150000,
          due_date: '2024-01-25',
          payment_status: 'pending' as const,
          last_reminder_sent: '2024-01-20',
        },
        {
          id: 2,
          policy_number: 'POL-2024-002',
          client_name: 'Jane Smith',
          premium_amount: 95000,
          due_date: '2024-01-30',
          payment_status: 'pending' as const,
        },
        {
          id: 3,
          policy_number: 'POL-2024-003',
          client_name: 'Mike Johnson',
          premium_amount: 50000,
          due_date: '2024-01-15',
          payment_status: 'overdue' as const,
          last_reminder_sent: '2024-01-18',
        },
        {
          id: 4,
          policy_number: 'POL-2024-004',
          client_name: 'Sarah Wilson',
          premium_amount: 75000,
          due_date: '2024-01-28',
          payment_status: 'pending' as const,
        },
      ];
    },
  });

  // Fetch reminder history
  const { data: reminderHistory = [] } = useQuery({
    queryKey: ['reminder-history'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return [
        {
          id: 1,
          policy_number: 'POL-2024-001',
          client_name: 'John Doe',
          sent_at: '2024-01-20T10:30:00Z',
          status: 'delivered' as const,
          message: 'Payment reminder sent for policy POL-2024-001',
        },
        {
          id: 2,
          policy_number: 'POL-2024-003',
          client_name: 'Mike Johnson',
          sent_at: '2024-01-18T14:20:00Z',
          status: 'delivered' as const,
          message: 'Overdue payment reminder sent for policy POL-2024-003',
        },
        {
          id: 3,
          policy_number: 'POL-2024-005',
          client_name: 'David Brown',
          sent_at: '2024-01-17T09:15:00Z',
          status: 'failed' as const,
          message: 'Failed to send reminder - invalid contact information',
        },
      ];
    },
  });

  // Send reminders mutation
  const sendRemindersMutation = useMutation({
    mutationFn: async (data: { policyIds: number[]; message?: string }) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      return { success: true, sentCount: data.policyIds.length };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminder-history'] });
      setSelectedPolicies([]);
      setCustomMessage('');
    },
  });

  const handlePolicySelection = (policyId: number) => {
    setSelectedPolicies(prev => 
      prev.includes(policyId) 
        ? prev.filter(id => id !== policyId)
        : [...prev, policyId]
    );
  };

  const handleSelectAll = () => {
    const pendingPolicies = policies.filter(p => p.payment_status !== 'paid').map(p => p.id);
    setSelectedPolicies(pendingPolicies);
  };

  const handleDeselectAll = () => {
    setSelectedPolicies([]);
  };

  const handleSendReminders = async () => {
    if (selectedPolicies.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one policy to send reminders.' });
      return;
    }

    setIsSending(true);
    setMessage(null);

    try {
      await sendRemindersMutation.mutateAsync({
        policyIds: selectedPolicies,
        message: customMessage || undefined,
      });
      setMessage({ type: 'success', text: `Successfully sent ${selectedPolicies.length} reminder(s)!` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to send reminders. Please try again.' });
    } finally {
      setIsSending(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      paid: 'bg-green-900/30 text-green-400 border-green-500/30',
      pending: 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30',
      overdue: 'bg-red-900/30 text-red-400 border-red-500/30',
    };
    return colors[status as keyof typeof colors] || colors.pending;
  };

  const getReminderStatusColor = (status: string) => {
    const colors = {
      sent: 'bg-blue-900/30 text-blue-400 border-blue-500/30',
      delivered: 'bg-green-900/30 text-green-400 border-green-500/30',
      failed: 'bg-red-900/30 text-red-400 border-red-500/30',
    };
    return colors[status as keyof typeof colors] || colors.sent;
  };

  if (policiesLoading) {
    return (
      <Layout title="Send Reminders">
        <div className="max-w-6xl mx-auto p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Send Reminders</h1>
            <p className="text-gray-400">Send payment reminders to clients</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-700 rounded w-1/4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Send Reminders">
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Send Reminders</h1>
          <p className="text-gray-400">Send payment reminders to clients</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-900/20 border border-green-500/30 text-green-400' 
              : 'bg-red-900/20 border border-red-500/30 text-red-400'
          }`}>
            {message.text}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Policies Selection */}
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-white">Select Policies</h3>
              <div className="flex space-x-2">
                <button
                  onClick={handleSelectAll}
                  className="px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                >
                  Select All
                </button>
                <button
                  onClick={handleDeselectAll}
                  className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                >
                  Deselect All
                </button>
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {policies.map((policy) => (
                <div
                  key={policy.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedPolicies.includes(policy.id)
                      ? 'border-orange-500 bg-orange-500/10'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                  onClick={() => handlePolicySelection(policy.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedPolicies.includes(policy.id)}
                        onChange={() => handlePolicySelection(policy.id)}
                        className="h-4 w-4 text-orange-500 focus:ring-orange-500 border-gray-600 rounded bg-gray-700"
                      />
                      <div>
                        <h4 className="text-white font-medium">{policy.policy_number}</h4>
                        <p className="text-gray-400 text-sm">{policy.client_name}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-white font-medium">
                        ₦{(policy.premium_amount / 1000).toFixed(0)}K
                      </div>
                      <div className="text-sm text-gray-400">
                        Due: {new Date(policy.due_date).toLocaleDateString()}
                      </div>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(policy.payment_status)}`}>
                        {policy.payment_status.charAt(0).toUpperCase() + policy.payment_status.slice(1)}
                      </span>
                    </div>
                  </div>
                  {policy.last_reminder_sent && (
                    <div className="mt-2 text-xs text-gray-400">
                      Last reminder: {new Date(policy.last_reminder_sent).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
              {policies.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-400">No policies requiring reminders found.</p>
                </div>
              )}
            </div>
          </div>

          {/* Reminder Configuration */}
          <div className="space-y-6">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Reminder Configuration</h3>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Custom Message (Optional)
                </label>
                <textarea
                  value={customMessage}
                  onChange={(e) => setCustomMessage(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-white placeholder-gray-400"
                  placeholder="Enter a custom message to include with the reminder..."
                />
                <p className="text-sm text-gray-400 mt-1">
                  Leave empty to use the default reminder message.
                </p>
              </div>

              <div className="mb-6">
                <h4 className="text-white font-medium mb-3">Selected Policies: {selectedPolicies.length}</h4>
                {selectedPolicies.length > 0 && (
                  <div className="bg-gray-700 rounded-lg p-3">
                    <p className="text-gray-300 text-sm">
                      Ready to send reminders to {selectedPolicies.length} client(s)
                    </p>
                  </div>
                )}
              </div>

              <button
                onClick={handleSendReminders}
                disabled={isSending || selectedPolicies.length === 0}
                className="w-full px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSending ? 'Sending Reminders...' : `Send Reminders (${selectedPolicies.length})`}
              </button>
            </div>

            {/* Reminder History */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Recent Reminder History</h3>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {reminderHistory.map((reminder) => (
                  <div key={reminder.id} className="border border-gray-700 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="text-white font-medium">{reminder.policy_number}</h4>
                        <p className="text-gray-400 text-sm">{reminder.client_name}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getReminderStatusColor(reminder.status)}`}>
                        {reminder.status.charAt(0).toUpperCase() + reminder.status.slice(1)}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm">{reminder.message}</p>
                    <div className="text-xs text-gray-400 mt-2">
                      Sent: {new Date(reminder.sent_at).toLocaleString()}
                    </div>
                  </div>
                ))}
                {reminderHistory.length === 0 && (
                  <div className="text-center py-4">
                    <p className="text-gray-400">No recent reminder history.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default withAuth(RemindersPage); 