import useSWR from 'swr';
import axios from 'axios';
import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useMemo } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const useApi = <T = any>(url: string | null) => {
  const { getAccessTokenSilently } = useAuth0();

  const api = useMemo(() => {
    const instance = axios.create({
      baseURL: API_BASE_URL,
    });

    instance.interceptors.request.use(async (config) => {
      const token = await getAccessTokenSilently();
      config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    return instance;
  }, [getAccessTokenSilently]);
  
  const fetcher = async (fetchUrl: string) => {
    const response = await api.get<T>(fetchUrl);
    return response.data;
  };

  const { data, error, isLoading, mutate } = useSWR<T>(url, fetcher);

  return { data, error, isLoading, mutate, api };
};

export default useApi; 