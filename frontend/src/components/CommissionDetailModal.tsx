'use client';

import React from 'react';

interface Commission {
  id: number;
  policy_number: string;
  client_name: string;
  premium_amount: number;
  commission_rate: number;
  commission_amount: number;
  payment_date: string;
  status: 'paid' | 'pending' | 'processing';
  payment_method: string;
  transaction_ref: string;
}

interface CommissionDetailModalProps {
  commission: Commission | null;
  onClose: () => void;
}

const CommissionDetailModal: React.FC<CommissionDetailModalProps> = ({ commission, onClose }) => {
  if (!commission) return null;

  const formatCurrency = (amount: number) => {
    return `₦${(amount / 1000).toFixed(1)}K`;
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return 'N/A';
    }
  };

  const getStatusConfig = (status: string) => {
    const configs = {
      paid: { bg: 'bg-green-900/30', text: 'text-green-400', border: 'border-green-500/30', label: 'Paid' },
      pending: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', border: 'border-yellow-500/30', label: 'Pending' },
      processing: { bg: 'bg-blue-900/30', text: 'text-blue-400', border: 'border-blue-500/30', label: 'Processing' },
    };
    return configs[status as keyof typeof configs] || configs.pending;
  };

  const statusConfig = getStatusConfig(commission.status);

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-white text-xl font-bold">Commission Details</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Status Badge */}
          <div className="flex justify-center">
            <span className={`px-4 py-2 rounded-full text-sm font-medium ${statusConfig.bg} ${statusConfig.text} border ${statusConfig.border}`}>
              {statusConfig.label}
            </span>
          </div>

          {/* Commission Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-700/50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-400 mb-1">Policy Number</label>
              <div className="text-white font-semibold">{commission.policy_number}</div>
            </div>

            <div className="bg-gray-700/50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-400 mb-1">Client Name</label>
              <div className="text-white font-semibold">{commission.client_name}</div>
            </div>

            <div className="bg-gray-700/50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-400 mb-1">Premium Amount</label>
              <div className="text-white font-semibold text-lg">{formatCurrency(commission.premium_amount)}</div>
            </div>

            <div className="bg-gray-700/50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-400 mb-1">Commission Rate</label>
              <div className="text-white font-semibold">{(commission.commission_rate * 100).toFixed(1)}%</div>
            </div>

            <div className="bg-gray-700/50 rounded-lg p-4 md:col-span-2">
              <label className="block text-sm font-medium text-gray-400 mb-1">Commission Amount</label>
              <div className="text-white font-semibold text-2xl text-orange-400">{formatCurrency(commission.commission_amount)}</div>
            </div>

            <div className="bg-gray-700/50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-400 mb-1">Payment Date</label>
              <div className="text-white">{formatDate(commission.payment_date)}</div>
            </div>

            <div className="bg-gray-700/50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-400 mb-1">Payment Method</label>
              <div className="text-white">{commission.payment_method}</div>
            </div>

            {commission.transaction_ref && (
              <div className="bg-gray-700/50 rounded-lg p-4 md:col-span-2">
                <label className="block text-sm font-medium text-gray-400 mb-1">Transaction Reference</label>
                <div className="text-white font-mono text-sm">{commission.transaction_ref}</div>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-gray-600 text-gray-300 rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommissionDetailModal;

