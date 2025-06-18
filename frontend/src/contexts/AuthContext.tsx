import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth0, Auth0ContextInterface, AppState } from '@auth0/auth0-react';

// Extended interface for development mode
interface ExtendedAuthInterface {
  user?: any;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginWithRedirect: () => Promise<void>;
  logout: (options?: any) => void;
  getAccessTokenSilently?: () => Promise<string>;
}

// create a context to hold the auth state
const AuthContext = createContext<ExtendedAuthInterface | null>(null);

// custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

// Development mode mock user
const mockUser = {
  name: 'Test User',
  email: 'test@example.com',
  picture: '',
  sub: 'dev-user-123'
};

// the provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth0 = useAuth0();
  const [devMode, setDevMode] = useState(false);
  const [devAuthenticated, setDevAuthenticated] = useState(false);

  // Check if we're in development mode (no Auth0 domain configured)
  useEffect(() => {
    const isDev = process.env.REACT_APP_DEV_MODE === 'true' || 
                  !process.env.REACT_APP_AUTH0_DOMAIN || 
                  process.env.NODE_ENV === 'development';
    setDevMode(isDev);
    if (isDev) {
      // Auto-authenticate in development mode
      setDevAuthenticated(true);
      console.log('Running in development mode with mock authentication');
    }
  }, []);

  // Development mode auth object
  const devAuth: ExtendedAuthInterface = {
    user: mockUser,
    isAuthenticated: devAuthenticated,
    isLoading: false,
    loginWithRedirect: async () => {
      setDevAuthenticated(true);
    },
    logout: () => {
      setDevAuthenticated(false);
    },
    getAccessTokenSilently: async () => {
      return 'dev-token-123';
    }
  };

  // Use development auth or Auth0 based on configuration
  const authValue = devMode ? devAuth : auth0;

  return (
    <AuthContext.Provider value={authValue}>
      {children}
    </AuthContext.Provider>
  );
};
