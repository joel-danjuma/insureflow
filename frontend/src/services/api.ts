import axios from 'axios';
import { LoginFormData } from '@/components/LoginForm';
import { SignUpFormData } from '@/components/SignUpForm';

// This will be the base URL for our backend
// For VPS deployment, use the current hostname with port 8000
// In development, it falls back to localhost:8000
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    // Browser environment - use current hostname with backend port
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000/api/v1`;
  }
  // Server-side rendering fallback
  return 'http://localhost:8000/api/v1';
};

const API_URL = getApiUrl();

const apiClient = axios.create({
  baseURL: API_URL,
  // withCredentials will be important for handling cookies if we use them for auth
  withCredentials: true,
});

// Add a request interceptor to automatically include the auth token
apiClient.interceptors.request.use((config) => {
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
apiClient.interceptors.response.use(
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
      const response = await apiClient.post('/auth/login', form, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Login failed');
      }
      throw new Error('An unexpected error occurred during login.');
    }
  },

  register: async (data: SignUpFormData) => {
    try {
      const response = await apiClient.post('/auth/register', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Registration failed');
      }
      throw new Error('An unexpected error occurred during registration.');
    }
  },

  getCurrentUser: async (token: string) => {
    try {
        const response = await apiClient.get('/users/me', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || 'Failed to fetch user');
        }
        throw new Error('An unexpected error occurred while fetching user data.');
    }
  },

  logout: async () => {
    // Clear local storage and session storage
    sessionStorage.removeItem('auth-storage');
    localStorage.removeItem('auth-storage');
    
    // Could also call a logout endpoint if the backend supports it
    // try {
    //   await apiClient.post('/auth/logout');
    // } catch (error) {
    //   console.warn('Logout endpoint call failed:', error);
    // }
  },
};

export const dashboardService = {
  getDashboardData: async () => {
    try {
      const response = await apiClient.get('/dashboard/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch dashboard data');
      }
      throw new Error('An unexpected error occurred while fetching dashboard data.');
    }
  },
};

export const brokerService = {
  getBrokerProfile: async () => {
    try {
      const response = await apiClient.get('/brokers/me');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch broker profile');
      }
      throw new Error('An unexpected error occurred while fetching broker profile.');
    }
  },
};

export const policyService = {
  getPolicies: async () => {
    try {
      const response = await apiClient.get('/policies/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch policies');
      }
      throw new Error('An unexpected error occurred while fetching policies.');
    }
  },
};

export const premiumService = {
  getPremiums: async () => {
    try {
      const response = await apiClient.get('/premiums/');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch premiums');
      }
      throw new Error('An unexpected error occurred while fetching premiums.');
    }
  },

  payPremium: async (premiumId: number) => {
    try {
      const response = await apiClient.post(`/premiums/${premiumId}/pay`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to pay premium');
      }
      throw new Error('An unexpected error occurred while processing payment.');
    }
  },
};

export const paymentService = {
  initiateBulkPayment: async (policyIds: number[]) => {
    try {
      const response = await apiClient.post('/payments/bulk-initiate', {
        policy_ids: policyIds,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to initiate bulk payment');
      }
      throw new Error('An unexpected error occurred while initiating bulk payment.');
    }
  },

  verifyPayment: async (transactionRef: string) => {
    try {
      const response = await apiClient.get(`/payments/verify/${transactionRef}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to verify payment');
      }
      throw new Error('An unexpected error occurred while verifying payment.');
    }
  },
};

export const reminderService = {
  sendReminders: async (data: { broker_ids?: number[], policy_ids?: number[] }) => {
    try {
      const response = await apiClient.post('/reminders/send', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to send reminders');
      }
      throw new Error('An unexpected error occurred while sending reminders.');
    }
  },

  getOutstandingPolicies: async () => {
    try {
      const response = await apiClient.get('/policies/outstanding');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch outstanding policies');
      }
      throw new Error('An unexpected error occurred while fetching outstanding policies.');
    }
  },
};

export default apiClient; 