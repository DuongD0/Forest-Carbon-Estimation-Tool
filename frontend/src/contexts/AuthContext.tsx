import { createContext, useContext, useState, ReactNode } from 'react';

// Define the authentication context type
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

// Define the user type
export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  login: async () => false,
  logout: () => {},
});

// Auth provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Auth provider component
export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      // In a real implementation, this would make an API call to the backend
      // For now, we'll simulate a successful login with mock data
      console.log(`Login attempt with email: ${email}`);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful login
      const mockUser: User = {
        id: 1,
        email,
        name: 'Forest Manager',
        role: 'admin',
      };
      
      setUser(mockUser);
      setIsAuthenticated(true);
      
      // Store auth token in localStorage (in a real app)
      localStorage.setItem('authToken', 'mock-jwt-token');
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('authToken');
  };

  // Provide the auth context to children components
  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);
