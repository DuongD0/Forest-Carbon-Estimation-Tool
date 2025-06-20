import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig, AxiosInstance } from 'axios';
import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useState } from 'react';

// fallback to REACT_APP_API_URL (used in Docker) if REACT_APP_API_BASE_URL is not set
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

console.log('API Base URL:', API_BASE_URL);

// Create authenticated API client for development mode
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication interceptor for development mode
apiClient.interceptors.request.use(
  async (config) => {
    try {
      // In development, use a mock token
      const token = 'dev-token-123';
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      // console.log('API Request:', config.method?.toUpperCase(), config.url, 'with token:', token);
    } catch (error) {
      console.error('Could not get access token', error);
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url, 'Data:', response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.message);
    console.error('Error Response:', error.response);
    console.error('Error Request:', error.request);
    console.error('Error Config:', error.config);
    
    // Check if it's a network error (no response)
    if (!error.response) {
      console.error('Network Error - No response received');
      error.message = 'Network Error';
    }
    
    return Promise.reject(error);
  }
);

const useApi = (): AxiosInstance | null => {
  const [api, setApi] = useState<AxiosInstance | null>(null);

  useEffect(() => {
    const apiInstance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // For development mode, add a mock token
    apiInstance.interceptors.request.use(
      async (config) => {
        try {
          // In development, use a mock token
          const token = 'dev-token-123';
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.error('Could not get access token', error);
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    setApi(apiInstance);
  }, []);

  return api;
};

// expose the underlying Axios client so legacy components can import { api }
export const api = apiClient;

// api service for authentication
export const authService = {
  login: async (credentials: any) => {
    const response = await apiClient.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('accessToken', response.data.access_token);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('accessToken');
  },
  getCurrentUser: async () => {
    // assumes you have a /users/me endpoint
    const response = await apiClient.get('/users/me');
    return response.data;
  }
};

// api service for projects
export const projectService = {
  getProjects: async () => {
    const response = await apiClient.get('/projects/');
    return response.data;
  },
  getProjectById: async (id: string) => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },
  createProject: async (projectData: any) => {
    const response = await apiClient.post('/projects/', projectData);
    return response.data;
  },
  updateProject: async (id: string, projectData: any) => {
    const response = await apiClient.put(`/projects/${id}`, projectData);
    return response.data;
  },
  deleteProject: async (id: string) => {
    const response = await apiClient.delete(`/projects/${id}`);
    return response.data;
  },
  calculateCarbon: async (id: string, imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    const response = await apiClient.post(`/projects/${id}/calculate_carbon`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  uploadShapefile: async (id: string, shapefileZip: File) => {
    const formData = new FormData();
    formData.append('file', shapefileZip);
    const response = await apiClient.put(`/projects/${id}/shapefile`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
};

// api service for forests
export const forestService = {
    getForestsByProject: async (projectId: number) => {
        const response = await apiClient.get(`/forests/?project_id=${projectId}`);
        return response.data;
    },
    getForestById: async (id: number) => {
        const response = await apiClient.get(`/forests/${id}`);
        return response.data;
    },
    // add other forest-related calls here (create, update, delete)
};

// api service for ecosystems
export const ecosystemService = {
  getEcosystems: async () => {
    const response = await apiClient.get('/ecosystems/');
    return response.data;
  },
  getEcosystemById: async (id: string) => {
    const response = await apiClient.get(`/ecosystems/${id}`);
    return response.data;
  }
};

// api service for carbon calculation
export const calculationService = {
  calculateArea: async (imageFile: File, params: any) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('params', JSON.stringify(params));
    const response = await apiClient.post('/calculate/area/form', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  calculateAreaWithForestType: async (imageryId: number, projectId: number, forestType: string | null) => {
    const response = await apiClient.post('/calculate/area', {
      imagery_id: imageryId,
      project_id: projectId,
      forest_type: forestType
    });
    return response.data;
  },
  calculateCredits: async (calculationData: any) => {
    const response = await apiClient.post('/calculate/credits', calculationData);
    return response.data;
  }
};

// api service for P2P marketplace
export const marketplaceService = {
  getListings: async () => {
    const response = await apiClient.get('/p2p/listings');
    return response.data;
  },
  createListing: async (listingData: any) => {
    const response = await apiClient.post('/p2p/listings', listingData);
    return response.data;
  },
  purchaseCredits: async (listingId: string, transactionData: any) => {
    const response = await apiClient.post(`/p2p/listings/${listingId}/purchase`, transactionData);
    return response.data;
  }
};

// api service for geospatial operations
export const geospatialService = {
  findProjectsNear: async (lat: number, lon: number, distance_km: number = 10) => {
    const response = await apiClient.get(`/geospatial/projects/near?lat=${lat}&lon=${lon}&distance_km=${distance_km}`);
    return response.data;
  }
};

// api service for export
export const exportService = {
  exportProjectGeoJSON: async (projectId: string) => {
    const response = await apiClient.get(`/export/project/${projectId}/geojson`);
    return response.data;
  }
};

export default useApi;
