import axios, { AxiosError } from 'axios';
import { LoginFormData } from '@/components/LoginForm';
import { SignUpFormData } from '@/components/SignUpForm';

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
    // Browser environment - use current hostname
    const { protocol, hostname, port } = window.location;
    
    // If we're on port 3000 (frontend dev), use port 8000 for backend
    if (port === '3000') {
      return `${protocol}//${hostname}:8000/api/v1`;
    }
    
    // For production (no port or port 80/443), Nginx routes /api/v1 to backend
    // So just use the same host without specifying a port
    if (!port || port === '80' || port === '443') {
      return `${protocol}//${hostname}/api/v1`;
    }
    
    // For any other port, keep it
    return `${protocol}//${hostname}:${port}/api/v1`;
  }
  // Server-side rendering fallback
  return 'http://backend:8000/api/v1';
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || getApiUrl();

// Debug logging for API URL
if (typeof window !== 'undefined') {
  console.log('🔧 API Base URL:', API_URL);
}

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
  getDashboardData: async () => {
    try {
      const response = await api.get('/dashboard/');
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching dashboard data');
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

export const insuranceService = {
  getInsuranceProfile: async () => {
    try {
      const response = await api.get('/insurance/me');
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching insurance firm profile');
    }
  },
};

export const userProfileService = {
  getUserProfile: async (userRole: string) => {
    try {
      let response;
      let endpoint;
        switch (userRole) {
          case 'BROKER':
            endpoint = '/brokers/me';
            response = await api.get(endpoint);
            break;
          case 'INSURANCE_ADMIN':
          case 'INSURANCE_ACCOUNTANT':
            endpoint = '/insurance/me';
            response = await api.get(endpoint);
            break;
          case 'ADMIN':
            endpoint = '/users/me';
            response = await api.get(endpoint);
            break;
          default:
            endpoint = '/users/me';
            response = await api.get(endpoint);
            break;
        }
      return response.data;
    } catch (error) {
      errorHandler(error, 'fetching user profile');
    }
  },
};

export const policyService = {
  getPolicies: async () => {
    try {
      const response = await api.get('/policies/');
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