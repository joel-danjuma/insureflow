import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface LocalPolicy {
  id: string;
  policy_name: string;
  policy_number: string;
  policy_type: string;
  start_date: string;
  due_date: string;
  duration_months: number;
  premium_amount: number;
  payment_frequency: string;
  first_payment_date: string;
  grace_period_days: number;
  company_name: string;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  rc_number: string;
  coverage_amount: number;
  coverage_items: string;
  beneficiaries: string;
  broker_notes: string;
  internal_tags: string;
  auto_renew: boolean;
  notify_broker_on_change: boolean;
  created_at: string;
}

interface PolicyState {
  policies: LocalPolicy[];
  addPolicy: (policy: LocalPolicy) => void;
  getPolicies: () => LocalPolicy[];
  clearPolicies: () => void;
}

const usePolicyStore = create<PolicyState>()(
  persist(
    (set, get) => ({
      policies: [],
      addPolicy: (policy) => set((state) => ({ policies: [policy, ...state.policies] })),
      getPolicies: () => get().policies,
      clearPolicies: () => set({ policies: [] }),
    }),
    {
      name: 'policy-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

export default usePolicyStore; 