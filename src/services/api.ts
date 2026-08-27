import axios from 'axios';

// The base URL should come from environment variables in production
// Example: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Add timeouts and other configs suitable for enterprise apps
  timeout: 10000, 
});

// Interceptor for auth tokens (simulated)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('spendshield_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor for handling global errors (e.g., 401s)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error("Unauthorized access. Redirecting to login...");
    }
    return Promise.reject(error);
  }
);
