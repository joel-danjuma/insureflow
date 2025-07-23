'use client';

import { useState, useEffect, useCallback } from 'react';
import { useQuery as useReactQuery } from '@tanstack/react-query';
import { dashboardService, brokerService, policyService, premiumService } from '@/services/api';
import { DashboardData, Broker, Policy, Premium } from '@/types/user';

interface QueryResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

// Mock data for fallbacks
const mockDashboardData: DashboardData = {
  kpis: {
    new_policies_this_month: 42,
    outstanding_premiums_total: 12500000,
    broker_count: 3,
  },
  recent_policies: [
    { policy_number: "POL-001-2024-0001", customer_name: "John Adebayo", broker: "SCIB" },
    { policy_number: "POL-002-2024-0002", customer_name: "Sarah Okafor", broker: "ARK Insurance" },
    { policy_number: "POL-001-2024-0003", customer_name: "Michael Johnson", broker: "IBN" },
    { policy_number: "POL-003-2024-0001", customer_name: "Grace Emeka", broker: "SCIB" },
    { policy_number: "POL-002-2024-0004", customer_name: "David Chen", broker: "ARK Insurance" },
  ]
};

const mockBroker: Broker = {
  id: 1,
  user_id: 2,
  name: "SCIB",
  license_number: "BRK-2023-001",
  agency_name: "Sovereign Capital Investment Banking",
  contact_email: "contact@scib.ng",
  contact_phone: "+234-801-234-5678",
  office_address: "Lagos, Nigeria",
  is_active: true
};

const mockPolicies: Policy[] = [
  {
    id: 1,
    policy_number: "POL-001-2024-0001",
    policy_type: "LIFE",
    customer_id: 1,
    broker_id: 1,
    status: "ACTIVE",
    start_date: "2024-01-15",
    end_date: "2025-01-15",
    coverage_amount: 5000000,
    premium_amount: 250000,
    customer: { full_name: "John Adebayo", email: "john@example.com" },
    broker: { name: "SCIB" }
  },
  {
    id: 2,
    policy_number: "POL-002-2024-0002", 
    policy_type: "AUTO",
    customer_id: 2,
    broker_id: 2,
    status: "ACTIVE",
    start_date: "2024-02-01",
    end_date: "2025-02-01",
    coverage_amount: 3000000,
    premium_amount: 180000,
    customer: { full_name: "Sarah Okafor", email: "sarah@example.com" },
    broker: { name: "ARK Insurance" }
  },
  {
    id: 3,
    policy_number: "POL-001-2024-0003",
    policy_type: "HEALTH",
    customer_id: 3,
    broker_id: 3, 
    status: "ACTIVE",
    start_date: "2024-03-10",
    end_date: "2025-03-10",
    coverage_amount: 2000000,
    premium_amount: 120000,
    customer: { full_name: "Michael Johnson", email: "michael@example.com" },
    broker: { name: "IBN" }
  },
  {
    id: 4,
    policy_number: "POL-004-2024-0001",
    policy_type: "PROPERTY",
    customer_id: 4,
    broker_id: 1,
    status: "ACTIVE",
    start_date: "2024-04-05",
    end_date: "2025-04-05",
    coverage_amount: 8000000,
    premium_amount: 320000,
    customer: { full_name: "Amara Okoye", email: "amara@example.com" },
    broker: { name: "SCIB" }
  },
  {
    id: 5,
    policy_number: "POL-005-2024-0001",
    policy_type: "BUSINESS",
    customer_id: 5,
    broker_id: 2,
    status: "ACTIVE",
    start_date: "2024-05-12",
    end_date: "2025-05-12",
    coverage_amount: 15000000,
    premium_amount: 600000,
    customer: { full_name: "Emeka Nwankwo", email: "emeka@example.com" },
    broker: { name: "ARK Insurance" }
  }
];

const mockPremiums: Premium[] = [
  {
    id: 1,
    policy_id: 1,
    amount: 250000,
    due_date: "2024-01-15",
    payment_status: "paid",
    billing_period_start: "2024-01-15",
    billing_period_end: "2024-02-15"
  },
  {
    id: 2,
    policy_id: 2,
    amount: 180000,
    due_date: "2024-02-01", 
    payment_status: "pending",
    billing_period_start: "2024-02-01",
    billing_period_end: "2024-03-01"
  },
  {
    id: 3,
    policy_id: 3,
    amount: 120000,
    due_date: "2024-03-10",
    payment_status: "paid",
    billing_period_start: "2024-03-10",
    billing_period_end: "2024-04-10"
  },
  {
    id: 4,
    policy_id: 4,
    amount: 320000,
    due_date: "2024-04-05",
    payment_status: "pending",
    billing_period_start: "2024-04-05",
    billing_period_end: "2024-05-05"
  },
  {
    id: 5,
    policy_id: 5,
    amount: 600000,
    due_date: "2024-05-12",
    payment_status: "overdue",
    billing_period_start: "2024-05-12",
    billing_period_end: "2024-06-12"
  }
];

// Custom hook with fetch function as argument
const useQuery = <T>(fetchFunction: () => Promise<T>, dependencies: unknown[] = []): QueryResult<T> => {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [fetchFunction]);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchData, ...dependencies]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch };
};

export default useQuery;

// React Query hooks for specific data fetching with mock fallbacks

// Dashboard data hook for Admin/Insurance Firm dashboard
export const useDashboardData = () => {
  return useReactQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      try {
        return await dashboardService.getDashboardData();
      } catch (error) {
        console.warn('Dashboard API failed, using mock data:', error);
        return mockDashboardData;
      }
    },
    staleTime: 30 * 1000, // 30 seconds (reduced from 5 minutes)
    retry: false, // Don't retry, use mock data on failure
    refetchOnWindowFocus: false,
  });
};

// Broker profile hook for Broker dashboard
export const useBrokerProfile = () => {
  return useReactQuery<Broker>({
    queryKey: ['broker', 'profile'],
    queryFn: async () => {
      try {
        return await brokerService.getBrokerProfile();
      } catch (error) {
        console.warn('Broker profile API failed, using mock data:', error);
        return mockBroker;
      }
    },
    staleTime: 30 * 1000, // 30 seconds (reduced)
    retry: false, // Don't retry, use mock data on failure
    refetchOnWindowFocus: false,
  });
};

// Policies hook for both dashboards
export const usePolicies = () => {
  return useReactQuery<Policy[]>({
    queryKey: ['policies'],
    queryFn: async () => {
      try {
        return await policyService.getPolicies();
      } catch (error) {
        console.warn('Policies API failed, using mock data:', error);
        return mockPolicies;
      }
    },
    staleTime: 30 * 1000, // 30 seconds (reduced)
    retry: false, // Don't retry, use mock data on failure
    refetchOnWindowFocus: false,
  });
};

// Premiums hook for payment tracking
export const usePremiums = () => {
  return useReactQuery<Premium[]>({
    queryKey: ['premiums'],
    queryFn: async () => {
      try {
        return await premiumService.getPremiums();
      } catch (error) {
        console.warn('Premiums API failed, using mock data:', error);
        return mockPremiums;
      }
    },
    staleTime: 30 * 1000, // 30 seconds (reduced)
    retry: false, // Don't retry, use mock data on failure
    refetchOnWindowFocus: false,
  });
}; 