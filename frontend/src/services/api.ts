import axios, { AxiosError } from 'axios';
import { LoginFormData, SignUpFormData } from '@/types/user';

// Centralized error handler
const errorHandler = (error: any, context: string): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    // Check for a detailed error message from the backend
    if (axiosError.response?.data?.detail) {
      // Handle cases where the detail might be a JSON string
      try {
        const detail = JSON.parse(axiosError.response.data.detail);
        if (Array.isArray(detail) && detail[0]?.msg) {
          throw new Error(detail[0].msg);
        }
      } catch (e) {
        // Not a JSON string, throw as is
        throw new Error(axiosError.response.data.detail);
      }
      throw new Error(axiosError.response.data.detail);
    }
    // Handle specific HTTP status codes
    if (axiosError.response?.status === 404) {
      throw new Error(`Not Found: The requested resource for ${context} was not found.`);
    }
    if (axiosError.response?.status === 401) {
      throw new Error('Unauthorized: Please check your login credentials.');
    }
    // Generic network error
    if (axiosError.message.includes('Network Error')) {
      throw new Error('Network Error: Could not connect to the server. Please check your connection and the server status.');
    }
  }
  // Fallback for non-Axios errors or other issues
  console.error(`An unexpected error occurred in ${context}:`, error);
  throw new Error(`An unexpected error occurred while ${context}.`);
};

// This will be the base URL for our backend
// For VPS deployment, use the current hostname with port 8000
// In development, it falls back to localhost:8000
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    // Browser environment - use current hostname with backend port
    const { protocol, hostname, port } = window.location;
    // If we're on port 3000 (frontend), use port 8000 for backend
    // If we're on a different port, assume backend is on same hostname
    const backendPort = port === '3000' ? '8000' : port;
    return `${protocol}//${hostname}:${backendPort}/api/v1`;
  }
  // Server-side rendering fallback
  return 'http://backend:8000/api/v1';
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || getApiUrl();

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // Increased timeout to 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
  // withCredentials will be important for handling cookies if we use them for auth
  withCredentials: true,
});

// Add a request interceptor to automatically include the auth token
api.interceptors.request.use((config) => {
  // Get token from session storage
  const authStorage = sessionStorage.getItem('auth-storage');
  if (authStorage) {
    try {
      const { state } = JSON.parse(authStorage);
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`;
      }
    } catch (error) {
      console.error('Error parsing auth storage:', error);
    }
  }
  return config;
});

// Add a response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      sessionStorage.removeItem('auth-storage');
      // Only redirect if we're not already on the login page
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (credentials: LoginFormData) => {
    // FastAPI's OAuth2PasswordRequestForm expects form data, not JSON.
    const form = new URLSearchParams();
    form.append('username', credentials.email);
    form.append('password', credentials.password);

    try {
      const response = await api.post('/auth/login', form, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'logging in');
    }
  },

  register: async (data: SignUpFormData) => {
    try {
      const response = await api.post('/auth/register', data);
      return response.data;
    } catch (error) {
      errorHandler(error, 'registering');
    }
  },

  getCurrentUser: async (token: string) => {
    try {
        const response = await api.get('/users/me', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        errorHandler(error, 'fetching user data');
    }
  },

  logout: async () => {
    // Clear local storage and session storage
    sessionStorage.removeItem('auth-storage');
    localStorage.removeItem('auth-storage');
    
    // Could also call a logout endpoint if the backend supports it
    // try {
    //   await api.post('/auth/logout');
    // } catch (error) {
    //   console.warn('Logout endpoint call failed:', error);
    // }
  },
};

export const dashboardService = {
  getDashboardData: async (userRole?: string) => {
    try {
      // Call role-specific dashboard endpoint
      let endpoint = '/dashboard/';
      
      if (userRole) {
        switch (userRole.toUpperCase()) {
          case 'BROKER':
          case 'BROKER_ADMIN':
          case 'BROKER_ACCOUNTANT':
            endpoint = '/dashboard/broker';
            break;
          case 'INSURANCE_ADMIN':
          case 'INSURANCE_ACCOUNTANT':
            endpoint = '/dashboard/insurance-firm';
            break;
          case 'ADMIN':
            endpoint = '/dashboard/admin';
            break;
          default:
            endpoint = '/dashboard/';
        }
      }
      
      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching dashboard data');
    }
  },

  // ✅ New service method
  getLatestPayments: async () => {
    try {
      const response = await api.get('/dashboard/latest-payments');
      return response.data;
    } catch (error) {
      console.error("Failed to fetch latest payments:", error);
      return [];
    }
  },
};

export const brokerService = {
  getBrokerProfile: async () => {
    try {
      const response = await api.get('/brokers/me');
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching broker profile');
    }
  },
};

export const userService = {
  createBrokerUser: async (userData: any) => {
    try {
      const response = await api.post('/users/create-broker', userData);
      return response.data;
    } catch (error) {
      errorHandler(error, 'creating broker user');
      throw error;
    }
  },
};

export const clientService = {
  createClient: async (clientData: any) => {
    try {
      // Create client using register endpoint with CUSTOMER role
      const registerData = {
        ...clientData,
        role: 'CUSTOMER',
        password: 'TempPassword123!', // Clients will need to set their password on first login
      };
      const response = await api.post('/auth/register', registerData);
      return response.data;
    } catch (error) {
      errorHandler(error, 'creating client');
      throw error;
    }
  },

  getClient: async (clientId: number) => {
    try {
      const response = await api.get(`/users/${clientId}`);
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching client');
      throw error;
    }
  },

  updateClient: async (clientId: number, clientData: any) => {
    try {
      const response = await api.put(`/users/${clientId}`, clientData);
      return response.data;
    } catch (error) {
      errorHandler(error, 'updating client');
      throw error;
    }
  },

  getClients: async (skip: number = 0, limit: number = 100) => {
    try {
      // Get clients for current broker by fetching policies and extracting unique customers
      // For now, we'll get all users with CUSTOMER role that are associated with broker's policies
      const response = await api.get('/users/', {
        params: { skip, limit, role: 'CUSTOMER' },
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching clients');
      throw error;
    }
  },
};

export const supportService = {
  createTicket: async (ticketData: { title: string; description: string; category: string; priority: string }) => {
    try {
      const response = await api.post('/support/tickets', ticketData);
      return response.data;
    } catch (error) {
      errorHandler(error, 'creating support ticket');
      throw error;
    }
  },

  getTickets: async (status?: string) => {
    try {
      const response = await api.get('/support/tickets', {
        params: status ? { status } : {},
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching support tickets');
      throw error;
    }
  },

  getTicketById: async (ticketId: number) => {
    try {
      const response = await api.get(`/support/tickets/${ticketId}`);
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching support ticket');
      throw error;
    }
  },

  // Admin methods
  getAllTickets: async (status?: string, priority?: string, category?: string) => {
    try {
      const response = await api.get('/support/admin/tickets', {
        params: { status, priority, category },
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching all support tickets');
      throw error;
    }
  },

  updateTicket: async (ticketId: number, updateData: { status?: string; admin_response?: string }) => {
    try {
      const response = await api.patch(`/support/admin/tickets/${ticketId}`, updateData);
      return response.data;
    } catch (error) {
      errorHandler(error, 'updating support ticket');
      throw error;
    }
  },
};

export const policyService = {
  getPolicies: async (skip: number = 0, limit: number = 100) => {
    try {
      const response = await api.get('/policies/', {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching policies');
    }
  },
};

export const premiumService = {
  getPremiums: async () => {
    try {
      const response = await api.get('/premiums/');
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching premiums');
    }
  },

  payPremium: async (premiumId: number) => {
    try {
      const response = await api.post(`/premiums/${premiumId}/pay`);
      return response.data;
    } catch (error) {
      errorHandler(error, 'processing payment');
    }
  },
};

export const paymentService = {
  initiateBulkPayment: async (policyIds: number[]) => {
    try {
      const response = await api.post('/payments/bulk-initiate', {
        policy_ids: policyIds,
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'initiating bulk payment');
    }
  },

  verifyPayment: async (transactionRef: string) => {
    try {
      const response = await api.get(`/payments/verify/${transactionRef}`);
      return response.data;
    } catch (error) {
      errorHandler(error, 'verifying payment');
    }
  },

  simulateBankTransfer: async (premiumId: number) => {
    try {
      const response = await api.post('/testing/simulate-payment', { premium_id: premiumId });
      return response.data;
    } catch (error) {
      errorHandler(error, 'simulating bank transfer');
      throw error;
    }
  },
};

export const reminderService = {
  sendAutomaticReminders: async (maxDaysOverdue: number = 30, reminderCooldownHours: number = 24) => {
    try {
      const response = await api.post('/reminders/send-auto', {
        max_days_overdue: maxDaysOverdue,
        reminder_cooldown_hours: reminderCooldownHours
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'sending automatic reminders');
    }
  },

  sendReminders: async (data: { broker_ids?: number[], policy_ids?: number[] }) => {
    try {
      // Use the legacy endpoint for backward compatibility
      const response = await api.post('/reminders/send', data);
      return response.data;
    } catch (error) {
      errorHandler(error, 'sending reminders');
    }
  },

  getOutstandingPolicies: async () => {
    try {
      const response = await api.get('/policies/outstanding');
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching outstanding policies');
    }
  },
};

export const notificationService = {
  getNotifications: async (unreadOnly: boolean = false) => {
    try {
      const response = await api.get('/notifications/', {
        params: { unread_only: unreadOnly }
      });
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching notifications');
    }
  },

  markAsRead: async (notificationId: number) => {
    try {
      const response = await api.post(`/notifications/${notificationId}/read`);
      return response.data;
    } catch (error) {
      errorHandler(error, 'marking notification as read');
    }
  },

  dismissNotification: async (notificationId: number) => {
    try {
      const response = await api.post(`/notifications/${notificationId}/dismiss`);
      return response.data;
    } catch (error) {
      errorHandler(error, 'dismissing notification');
    }
  },

  getUnreadCount: async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching unread count');
    }
  },
};

export async function simulatePolicyPayment(policyId: number) {
  const res = await api.post(`/policies/${policyId}/simulate_payment`);
  return res.data;
}

export default api; 