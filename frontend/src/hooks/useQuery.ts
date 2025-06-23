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

// Custom hook with fetch function as argument
const useQuery = <T>(fetchFunction: () => Promise<T>, dependencies: any[] = []): QueryResult<T> => {
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
  }, [...dependencies, fetchData]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch };
};

export default useQuery;

// React Query hooks for specific data fetching

// Dashboard data hook for Admin/Insurance Firm dashboard
export const useDashboardData = () => {
  return useReactQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: dashboardService.getDashboardData,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

// Broker profile hook for Broker dashboard
export const useBrokerProfile = () => {
  return useReactQuery<Broker>({
    queryKey: ['broker', 'profile'],
    queryFn: brokerService.getBrokerProfile,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
};

// Policies hook for both dashboards
export const usePolicies = () => {
  return useReactQuery<Policy[]>({
    queryKey: ['policies'],
    queryFn: policyService.getPolicies,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
};

// Premiums hook for payment tracking
export const usePremiums = () => {
  return useReactQuery<Premium[]>({
    queryKey: ['premiums'],
    queryFn: premiumService.getPremiums,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
}; 