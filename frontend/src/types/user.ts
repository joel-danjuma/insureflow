export enum UserRole {
  ADMIN = 'admin',
  BROKER = 'broker',
  CUSTOMER = 'customer',
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuthUser {
  user: User;
  access_token: string;
}

// Dashboard Data Types
export interface DashboardKPIs {
  new_policies_this_month: number;
  outstanding_premiums_total: number;
  broker_count: number;
}

export interface RecentPolicy {
  policy_number: string;
  customer_name: string;
  broker: string;
}

export interface DashboardData {
  kpis: DashboardKPIs;
  recent_policies: RecentPolicy[];
}

// Broker Types  
export interface Broker {
  id: number;
  user_id: number;
  name: string;
  license_number: string;
  agency_name?: string;
  contact_email: string;
  contact_phone?: string;
  office_address?: string;
  is_active: boolean;
}

// Policy Types
export interface Policy {
  id: number;
  policy_number: string;
  policy_type: string;
  customer_id: number;
  broker_id?: number;
  coverage_amount: number;
  premium_amount: number;
  start_date: string;
  end_date: string;
  status: string;
  customer?: {
    full_name: string;
    email: string;
  };
  broker?: {
    name: string;
  };
}

// Premium Types
export interface Premium {
  id: number;
  policy_id: number;
  amount: number;
  due_date: string;
  payment_status: string;
  billing_period_start: string;
  billing_period_end: string;
  policy?: Policy;
} 