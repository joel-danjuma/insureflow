'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import useAuthStore from '@/store/authStore';
import { usePremiums } from '@/hooks/useQuery';
import { formatNaira } from '@/utils/currency';
import Layout from '@/components/Layout';

export default function PaymentsPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [selectedPremium, setSelectedPremium] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const { data: premiums, isLoading: premiumsLoading } = usePremiums();

  // Filter unpaid premiums with validation
  const unpaidPremiums = premiums?.filter(premium => {
    // Validate premium object exists and has required properties
    if (!premium || !premium.payment_status) return false;
    const status = premium.payment_status;
    return status === 'PENDING' || status === 'OVERDUE';
  }) || [];

  const handlePayPremium = async (premium: any) => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    setSelectedPremium(premium);

    try {
      const response = await fetch(`/api/v1/payments/initiate/${premium.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        if (result.payment_url) {
          // Redirect to Squad Co payment page
          window.location.href = result.payment_url;
        } else {
          throw new Error('No payment URL received');
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Payment initiation failed');
      }
    } catch (error) {
      console.error('Payment error:', error);
      alert(`Payment failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
      setSelectedPremium(null);
    }
  };

  const getStatusColor = (status: string | undefined | null) => {
    switch (status) {
      case 'PENDING':
        return 'text-yellow-400 bg-yellow-400/10';
      case 'OVERDUE':
        return 'text-red-400 bg-red-400/10';
      case 'PAID':
        return 'text-green-400 bg-green-400/10';
      default:
        return 'text-gray-400 bg-gray-400/10';
    }
  };

  // Helper function to safely format dates
  const formatDate = (dateString: string | undefined | null) => {
    if (!dateString) {
      return 'N/A';
    }
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' });
    } catch (e) {
      return 'Invalid Date';
    }
  };

  if (premiumsLoading) {
    return (
      <Layout title="Payments">
        <div className="space-y-6">
          <h1 className="text-white text-[28px] font-bold leading-tight tracking-[-0.015em]">Payments</h1>
          <div className="animate-pulse">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="h-4 bg-gray-700 rounded w-1/4 mb-4"></div>
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 bg-gray-700 rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Payments">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-white text-[28px] font-bold leading-tight tracking-[-0.015em]">Payments</h1>
            <p className="text-gray-400 text-sm font-normal leading-normal">
              Manage your premium payments and view payment history.
            </p>
          </div>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
          >
            ← Back
          </button>
        </div>

        {/* Unpaid Premiums */}
        {unpaidPremiums.length > 0 && (
          <div className="bg-gray-800 rounded-xl border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-white text-xl font-semibold">Outstanding Payments</h2>
              <p className="text-gray-400 text-sm mt-1">
                You have {unpaidPremiums.length} pending payment(s)
              </p>
            </div>
            
            <div className="divide-y divide-gray-700">
              {unpaidPremiums.map((premium) => {
                // Skip invalid premium records
                if (!premium || !premium.id) return null;
                
                const isSelected = selectedPremium?.id === premium.id;
                
                return (
                  <div key={premium.id} className="p-6 hover:bg-gray-750 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-white font-semibold">
                            {premium.policy?.policy_name || 'Unknown Policy'}
                          </h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(premium?.payment_status)}`}>
                            {premium?.payment_status || 'Unknown'}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-400">Policy Number:</span>
                            <div className="text-white font-mono">
                              {premium.policy?.policy_number || 'N/A'}
                            </div>
                          </div>
                          
                          <div>
                            <span className="text-gray-400">Due Date:</span>
                            <div className="text-white">
                              {formatDate(premium?.due_date)}
                            </div>
                          </div>
                          
                          <div>
                            <span className="text-gray-400">Amount:</span>
                            <div className="text-white font-semibold">
                              {formatNaira(premium?.amount || 0)}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="ml-6">
                        <button
                          onClick={() => handlePayPremium(premium)}
                          disabled={isProcessing}
                          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                            isSelected
                              ? 'bg-orange-600 text-white cursor-not-allowed'
                              : 'bg-orange-500 hover:bg-orange-600 text-white'
                          }`}
                        >
                          {isSelected ? (
                            <div className="flex items-center gap-2">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                              Processing...
                            </div>
                          ) : (
                            'Pay Now'
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* No Unpaid Premiums */}
        {unpaidPremiums.length === 0 && (
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-12 text-center">
            <div className="text-green-400 text-6xl mb-4">✅</div>
            <h2 className="text-white text-2xl font-bold mb-2">All Caught Up!</h2>
            <p className="text-gray-400 mb-6">
              You have no outstanding payments at this time.
            </p>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-6 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors"
            >
              Return to Dashboard
            </button>
          </div>
        )}

        {/* Payment History Section */}
        <div className="bg-gray-800 rounded-xl border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-white text-xl font-semibold">Recent Payment History</h2>
          </div>
          
          <div className="p-6">
            {premiums && premiums.length > 0 ? (
              <div className="space-y-4">
                {premiums.slice(0, 5).map((premium) => {
                  // Skip invalid premium records
                  if (!premium || !premium.id) return null;
                  
                  return (
                    <div key={premium.id} className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                      <div>
                        <div className="text-white font-medium">
                          {premium.policy?.policy_name || 'Unknown Policy'}
                        </div>
                        <div className="text-gray-400 text-sm">
                          {formatDate(premium?.due_date)}
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-white font-semibold">
                          {formatNaira(premium?.amount || 0)}
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(premium?.payment_status)}`}>
                          {premium?.payment_status || 'Unknown'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-400 text-lg mb-2">No payment history</div>
                <p className="text-gray-500 text-sm">Your payment history will appear here once you make payments.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}