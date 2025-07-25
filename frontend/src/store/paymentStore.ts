import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface PaymentRecord {
  id: string;
  brokerId: number;
  brokerName: string;
  totalAmount: number;
  policies: Array<{
    policyId: number;
    policyNumber: string;
    customerName: string;
    amount: number;
  }>;
  paymentMethod: 'bank_transfer' | 'ussd';
  status: 'completed' | 'pending' | 'failed';
  completedAt: string;
}

interface PaymentState {
  payments: PaymentRecord[];
  addPayment: (payment: PaymentRecord) => void;
  getPayments: () => PaymentRecord[];
  clearPayments: () => void;
  getPaymentsForBroker: (brokerId: number) => PaymentRecord[];
}

const usePaymentStore = create<PaymentState>()(
  persist(
    (set, get) => ({
      payments: [],
      addPayment: (payment) => set((state) => ({ payments: [payment, ...state.payments] })),
      getPayments: () => get().payments,
      clearPayments: () => set({ payments: [] }),
      getPaymentsForBroker: (brokerId) => get().payments.filter(p => p.brokerId === brokerId),
    }),
    {
      name: 'payment-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

export default usePaymentStore; 