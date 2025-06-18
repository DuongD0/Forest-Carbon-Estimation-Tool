import { P2PListing, Transaction } from '../types';
import axios from 'axios';

// fallback to REACT_APP_API_URL (used in Docker) if REACT_APP_API_BASE_URL is not set
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication interceptor for development mode
api.interceptors.request.use(
  async (config) => {
    try {
      // In development, use a mock token
      const token = 'dev-token-123';
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      // console.log('P2P API Request:', config.method?.toUpperCase(), config.url, 'with token:', token);
    } catch (error) {
      console.error('Could not get access token', error);
    }
    return config;
  },
  (error) => {
    console.error('P2P Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    // console.log('P2P API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('P2P API Error:', error.response?.status, error.response?.data, 'for URL:', error.config?.url);
    return Promise.reject(error);
  }
);

export const getP2PListings = async (): Promise<P2PListing[]> => {
  const response = await api.get('/p2p/listings');
  return response.data;
};

export const purchaseCredits = async (listingId: string, quantity: number): Promise<Transaction> => {
  const response = await api.post(`/p2p/listings/${listingId}/purchase`, { quantity });
  return response.data;
}; 