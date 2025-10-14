'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

interface PaymentResult {
  transactionRef?: string;
  status?: string;
  amount?: string;
  reason?: string;
  currency?: string;
  customerEmail?: string;
  customerName?: string;
}

type PaymentStatus = 'loading' | 'success' | 'failed' | 'cancelled';

export default function PaymentComplete() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<PaymentStatus>('loading');
  const [transactionData, setTransactionData] = useState<PaymentResult>({});

  useEffect(() => {
    // Get URL parameters from Squad Co redirect
    const transactionRef = searchParams.get('transaction_ref') || searchParams.get('txref');
    const paymentStatus = searchParams.get('status') || searchParams.get('transaction_status');
    const amount = searchParams.get('amount');
    const reason = searchParams.get('reason') || searchParams.get('message');
    const currency = searchParams.get('currency') || 'NGN';
    const customerEmail = searchParams.get('customer_email');
    const customerName = searchParams.get('customer_name');

    setTransactionData({
      transactionRef,
      status: paymentStatus,
      amount,
      reason,
      currency,
      customerEmail,
      customerName
    });

    // Determine status based on Squad response
    if (paymentStatus === 'success' || paymentStatus === 'successful' || paymentStatus === 'completed') {
      setStatus('success');
    } else if (paymentStatus === 'failed' || paymentStatus === 'error' || paymentStatus === 'declined') {
      setStatus('failed');
    } else if (paymentStatus === 'cancelled' || paymentStatus === 'canceled' || paymentStatus === 'abandoned') {
      setStatus('cancelled');
    } else {
      // If no clear status, default to failed for safety
      setStatus('failed');
    }

    // Optional: Send transaction data to backend for verification
    if (transactionRef) {
      verifyTransaction(transactionRef);
    }
  }, [searchParams]);

  const verifyTransaction = async (transactionRef: string) => {
    try {
      // Optional: Call your backend to verify the transaction
      const response = await fetch(`/api/v1/payments/verify/${transactionRef}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const verificationResult = await response.json();
        console.log('Transaction verified:', verificationResult);
        // You might want to update the UI based on verification result
      }
    } catch (error) {
      console.error('Transaction verification failed:', error);
      // Don't change the UI status based on verification failure
      // The redirect status should be the source of truth
    }
  };

  const handleReturnToDashboard = () => {
    router.push('/dashboard');
  };

  const handleRetryPayment = () => {
    // Redirect to payments page or specific premium payment
    router.push('/payments');
  };

  const handleViewTransaction = () => {
    // Redirect to transaction details page
    if (transactionData.transactionRef) {
      router.push(`/transactions/${transactionData.transactionRef}`);
    }
  };

  const formatAmount = (amount: string | undefined, currency: string = 'NGN') => {
    if (!amount) return 'N/A';
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return amount;
    
    if (currency === 'NGN') {
      return `₦${numAmount.toLocaleString()}`;
    }
    return `${currency} ${numAmount.toLocaleString()}`;
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <div className="text-white text-lg">Processing payment result...</div>
          <div className="text-gray-400 text-sm mt-2">Please wait while we verify your payment</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 max-w-lg w-full">
        
        {/* Success State */}
        {status === 'success' && (
          <div className="text-center">
            <div className="text-green-400 text-6xl mb-6">✅</div>
            <h1 className="text-white text-3xl font-bold mb-4">Payment Successful!</h1>
            <p className="text-gray-300 text-lg mb-6">
              Your payment has been processed successfully. Thank you for your payment!
            </p>
            
            {/* Transaction Details */}
            <div className="bg-gray-700 rounded-lg p-4 mb-6 text-left">
              <h3 className="text-white font-semibold mb-3">Transaction Details</h3>
              
              {transactionData.transactionRef && (
                <div className="flex justify-between py-2 border-b border-gray-600">
                  <span className="text-gray-400">Transaction ID:</span>
                  <span className="text-white font-mono text-sm">{transactionData.transactionRef}</span>
                </div>
              )}
              
              {transactionData.amount && (
                <div className="flex justify-between py-2 border-b border-gray-600">
                  <span className="text-gray-400">Amount:</span>
                  <span className="text-green-400 font-semibold">
                    {formatAmount(transactionData.amount, transactionData.currency)}
                  </span>
                </div>
              )}
              
              {transactionData.customerEmail && (
                <div className="flex justify-between py-2 border-b border-gray-600">
                  <span className="text-gray-400">Email:</span>
                  <span className="text-white">{transactionData.customerEmail}</span>
                </div>
              )}
              
              <div className="flex justify-between py-2">
                <span className="text-gray-400">Status:</span>
                <span className="text-green-400 font-semibold">Successful</span>
              </div>
            </div>
          </div>
        )}

        {/* Failed State */}
        {status === 'failed' && (
          <div className="text-center">
            <div className="text-red-400 text-6xl mb-6">❌</div>
            <h1 className="text-white text-3xl font-bold mb-4">Payment Failed</h1>
            <p className="text-gray-300 text-lg mb-4">
              Unfortunately, your payment could not be processed.
            </p>
            
            {transactionData.reason && (
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-6">
                <p className="text-red-300 text-sm">
                  <strong>Reason:</strong> {transactionData.reason}
                </p>
              </div>
            )}
            
            {transactionData.transactionRef && (
              <p className="text-gray-400 text-sm mb-6">
                Reference: {transactionData.transactionRef}
              </p>
            )}
          </div>
        )}

        {/* Cancelled State */}
        {status === 'cancelled' && (
          <div className="text-center">
            <div className="text-yellow-400 text-6xl mb-6">⚠️</div>
            <h1 className="text-white text-3xl font-bold mb-4">Payment Cancelled</h1>
            <p className="text-gray-300 text-lg mb-6">
              You cancelled the payment process. No charges have been made to your account.
            </p>
            
            {transactionData.transactionRef && (
              <p className="text-gray-400 text-sm mb-6">
                Reference: {transactionData.transactionRef}
              </p>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center mt-8">
          <button
            onClick={handleReturnToDashboard}
            className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
          >
            Return to Dashboard
          </button>
          
          {status === 'success' && transactionData.transactionRef && (
            <button
              onClick={handleViewTransaction}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              View Transaction
            </button>
          )}
          
          {(status === 'failed' || status === 'cancelled') && (
            <button
              onClick={handleRetryPayment}
              className="px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors"
            >
              Try Again
            </button>
          )}
        </div>

        {/* Additional Help */}
        {status === 'failed' && (
          <div className="mt-8 pt-6 border-t border-gray-700">
            <h4 className="text-white font-semibold mb-2">Need Help?</h4>
            <p className="text-gray-400 text-sm mb-3">
              If you continue to experience issues with your payment, please contact our support team.
            </p>
            <div className="flex flex-col sm:flex-row gap-2 text-sm">
              <a 
                href="mailto:support@insureflow.tech" 
                className="text-orange-400 hover:text-orange-300 transition-colors"
              >
                support@insureflow.tech
              </a>
              <span className="text-gray-500 hidden sm:inline">|</span>
              <a 
                href="tel:+2341234567890" 
                className="text-orange-400 hover:text-orange-300 transition-colors"
              >
                +234 123 456 7890
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
