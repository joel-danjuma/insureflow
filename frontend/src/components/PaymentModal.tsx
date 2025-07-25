'use client';

import React, { useState } from 'react';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCompletePayment: (paymentMethod: 'bank_transfer' | 'ussd') => void;
  selectedPolicies: Array<{
    id: string;
    policyNumber: string;
    customerName: string;
    premiumAmount: string;
    premiumAmountRaw: number;
  }>;
  totalAmount: number;
  isLoading: boolean;
  isSuccess: boolean;
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  onCompletePayment,
  selectedPolicies,
  totalAmount,
  isLoading,
  isSuccess
}) => {
  const [selectedMethod, setSelectedMethod] = useState<'bank_transfer' | 'ussd' | null>(null);

  if (!isOpen) return null;

  const formatNaira = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl border border-gray-700 max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-xl font-bold">Complete Payment</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Success State */}
          {isSuccess && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-green-400 text-xl font-bold mb-2">Payment Successful!</h3>
              <p className="text-gray-300">Your payment has been processed successfully.</p>
            </div>
          )}

          {/* Loading State */}
          {isLoading && !isSuccess && (
            <div className="text-center py-8">
              <div className="animate-spin h-12 w-12 border-4 border-orange-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-white text-lg">Processing payment...</p>
            </div>
          )}

          {/* Payment Content */}
          {!isLoading && !isSuccess && (
            <>
              {/* Selected Policies */}
              <div className="mb-6">
                <h3 className="text-white font-semibold mb-3">Selected Policies</h3>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {selectedPolicies.map((policy) => (
                    <div key={policy.id} className="bg-gray-700 rounded-lg p-3">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="text-white font-medium">{policy.customerName}</p>
                          <p className="text-gray-400 text-sm">{policy.policyNumber}</p>
                        </div>
                        <p className="text-orange-400 font-semibold">{policy.premiumAmount}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Total Amount */}
              <div className="bg-gray-700 rounded-lg p-4 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Total Amount:</span>
                  <span className="text-white text-xl font-bold">{formatNaira(totalAmount)}</span>
                </div>
              </div>

              {/* Payment Methods */}
              <div className="mb-6">
                <h3 className="text-white font-semibold mb-3">Select Payment Method</h3>
                
                {/* Bank Transfer */}
                <div 
                  className={`border rounded-lg p-4 mb-3 cursor-pointer transition-colors ${
                    selectedMethod === 'bank_transfer' 
                      ? 'border-orange-500 bg-orange-500/10' 
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => setSelectedMethod('bank_transfer')}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                        <span className="text-white text-sm font-bold">B</span>
                      </div>
                      <div>
                        <p className="text-white font-medium">Bank Transfer</p>
                        <p className="text-gray-400 text-sm">Pay with bank transfer</p>
                      </div>
                    </div>
                    <input
                      type="radio"
                      checked={selectedMethod === 'bank_transfer'}
                      onChange={() => setSelectedMethod('bank_transfer')}
                      className="text-orange-500"
                    />
                  </div>
                  
                  {selectedMethod === 'bank_transfer' && (
                    <div className="mt-3 p-3 bg-gray-600 rounded-lg">
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Bank:</span>
                          <span className="text-white font-semibold">Squad Bank</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Account Number:</span>
                          <span className="text-white font-semibold">1234567890</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Account Name:</span>
                          <span className="text-white font-semibold">SCIB-AXA SETTLEMENT ACCOUNT</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* USSD */}
                <div 
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedMethod === 'ussd' 
                      ? 'border-orange-500 bg-orange-500/10' 
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => setSelectedMethod('ussd')}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center mr-3">
                        <span className="text-white text-sm font-bold">U</span>
                      </div>
                      <div>
                        <p className="text-white font-medium">USSD</p>
                        <p className="text-gray-400 text-sm">Pay with USSD code</p>
                      </div>
                    </div>
                    <input
                      type="radio"
                      checked={selectedMethod === 'ussd'}
                      onChange={() => setSelectedMethod('ussd')}
                      className="text-orange-500"
                    />
                  </div>
                  
                  {selectedMethod === 'ussd' && (
                    <div className="mt-3 p-3 bg-gray-600 rounded-lg">
                      <div className="text-center">
                        <p className="text-white font-bold text-lg mb-2">*123*456#</p>
                        <p className="text-gray-400 text-sm">Dial this code on your phone to complete payment</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Complete Payment Button */}
              <button
                onClick={() => selectedMethod && onCompletePayment(selectedMethod)}
                disabled={!selectedMethod}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  selectedMethod
                    ? 'bg-orange-500 hover:bg-orange-600 text-white'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
              >
                Complete Payment
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentModal; 