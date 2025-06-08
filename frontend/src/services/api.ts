import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig, AxiosInstance } from 'axios';
import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useState } from 'react';

// Define the base URL for API calls
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const useApi = (): AxiosInstance | null => {
  const { getAccessTokenSilently } = useAuth0();
  const [api, setApi] = useState<AxiosInstance | null>(null);

  useEffect(() => {
    const apiInstance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    apiInstance.interceptors.request.use(
      async (config) => {
        try {
          const token = await getAccessTokenSilently();
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
  }, [getAccessTokenSilently]);

  return api;
};

// API service for authentication
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
    // This assumes you have a /users/me endpoint
    const response = await apiClient.get('/users/me');
    return response.data;
  }
};

// API service for projects
export const projectService = {
  getProjects: async () => {
    const response = await apiClient.get('/projects/');
    return response.data;
  },
  getProjectById: async (id: number) => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },
  createProject: async (projectData: any) => {
    const response = await apiClient.post('/projects/', projectData);
    return response.data;
  },
  updateProject: async (id: number, projectData: any) => {
    const response = await apiClient.put(`/projects/${id}`, projectData);
    return response.data;
  },
  deleteProject: async (id: number) => {
    const response = await apiClient.delete(`/projects/${id}`);
    return response.data;
  },
  calculateCarbon: async (id: number) => {
    const response = await apiClient.post(`/projects/${id}/calculate`);
    return response.data;
  }
};

// API service for forests
export const forestService = {
    getForestsByProject: async (projectId: number) => {
        const response = await apiClient.get(`/forests/?project_id=${projectId}`);
        return response.data;
    },
    getForestById: async (id: number) => {
        const response = await apiClient.get(`/forests/${id}`);
        return response.data;
    }
    // Add other forest-related calls here (create, update, delete)
};

// API service for imagery
export const imageryService = {
    getImageryByProject: async (projectId: number) => {
        const response = await apiClient.get(`/imagery/?project_id=${projectId}`);
        return response.data;
    },
    getImageryById: async (id: number) => {
        const response = await apiClient.get(`/imagery/${id}`);
        return response.data;
    },
    uploadImagery: async (formData: FormData) => {
        const response = await apiClient.post('/imagery/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },
    processImagery: async (id: number) => {
        const response = await apiClient.post(`/imagery/${id}/process`);
        return response.data;
    },
    deleteImagery: async (id: number) => {
        const response = await apiClient.delete(`/imagery/${id}`);
        return response.data;
    }
};

export default useApi;
