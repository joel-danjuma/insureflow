'use client';

import React, { useState } from 'react';

interface PayoutRequestModalProps {
  totalPaidCommission: number;
  onClose: () => void;
  onSubmit?: (amount: number, accountDetails: any) => Promise<void>;
}

const PayoutRequestModal: React.FC<PayoutRequestModalProps> = ({ 
  totalPaidCommission, 
  onClose,
  onSubmit 
}) => {
  const [requestedAmount, setRequestedAmount] = useState<number>(totalPaidCommission);
  const [accountNumber, setAccountNumber] = useState('');
  const [accountName, setAccountName] = useState('');
  const [bankName, setBankName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatCurrency = (amount: number) => {
    return `₦${(amount / 1000).toFixed(1)}K`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate form
    if (!accountNumber || !accountName || !bankName) {
      setError('Please fill in all account details.');
      return;
    }

    if (requestedAmount <= 0) {
      setError('Requested amount must be greater than zero.');
      return;
    }

    if (requestedAmount > totalPaidCommission) {
      setError(`Requested amount cannot exceed available commission (${formatCurrency(totalPaidCommission)}).`);
      return;
    }

    setIsSubmitting(true);

    try {
      const accountDetails = {
        account_number: accountNumber,
        account_name: accountName,
        bank_name: bankName,
      };

      if (onSubmit) {
        await onSubmit(requestedAmount, accountDetails);
      } else {
        // Default behavior: just log and close
        console.log('Payout request:', {
          amount: requestedAmount,
          accountDetails,
        });
        alert('Payout request submitted successfully! This is a demo - actual integration would send to backend.');
      }

      onClose();
    } catch (err: any) {
      console.error('Error submitting payout request:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to submit payout request. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-white text-xl font-bold">Request Payout</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Available Commission Info */}
        <div className="bg-gray-700/50 rounded-lg p-4 mb-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Available Commission:</span>
            <span className="text-white font-bold text-xl text-green-400">
              {formatCurrency(totalPaidCommission)}
            </span>
          </div>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-6">
            <div className="text-red-400 text-sm">{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Requested Amount */}
          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Requested Amount <span className="text-red-400">*</span>
            </label>
            <input
              type="number"
              value={requestedAmount}
              onChange={(e) => setRequestedAmount(Number(e.target.value))}
              min={0}
              max={totalPaidCommission}
              step={100}
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
            <p className="text-gray-400 text-xs mt-1">
              Maximum: {formatCurrency(totalPaidCommission)}
            </p>
          </div>

          {/* Account Details */}
          <div className="border-t border-gray-700 pt-4">
            <h4 className="text-white font-semibold mb-4">Bank Account Details</h4>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Account Number <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={accountNumber}
                  onChange={(e) => setAccountNumber(e.target.value.replace(/\D/g, ''))}
                  required
                  placeholder="1234567890"
                  maxLength={10}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Account Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                  required
                  placeholder="John Doe"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Bank Name <span className="text-red-400">*</span>
                </label>
                <select
                  value={bankName}
                  onChange={(e) => setBankName(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="">Select Bank</option>
                  <option value="Access Bank">Access Bank</option>
                  <option value="First Bank">First Bank</option>
                  <option value="GTBank">GTBank</option>
                  <option value="Zenith Bank">Zenith Bank</option>
                  <option value="UBA">UBA</option>
                  <option value="Fidelity Bank">Fidelity Bank</option>
                  <option value="Stanbic IBTC">Stanbic IBTC</option>
                  <option value="Union Bank">Union Bank</option>
                  <option value="Wema Bank">Wema Bank</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-2 border border-gray-600 text-gray-300 rounded-lg font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                isSubmitting
                  ? 'bg-gray-600 cursor-not-allowed text-gray-400'
                  : 'bg-orange-500 hover:bg-orange-600 text-white'
              }`}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PayoutRequestModal;

