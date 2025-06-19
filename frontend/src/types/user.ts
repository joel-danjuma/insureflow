export enum UserRole {
  INSURANCE_FIRM = 'insurance-firm',
  BROKER = 'broker',
  CUSTOMER = 'customer',
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
} 