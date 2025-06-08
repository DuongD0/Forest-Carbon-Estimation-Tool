import React, { createContext, useContext } from 'react';
import { useAuth0, Auth0ContextInterface, AppState } from '@auth0/auth0-react';

// Create a context to hold the auth state
const AuthContext = createContext<Auth0ContextInterface | null>(null);

// Custom hook to use the auth context
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

// The provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth0 = useAuth0();

  // The onRedirectCallback is used to handle the user's return to the application after login.
  // We don't need to do anything special here, but it's required by the provider.
  const onRedirectCallback = (appState?: AppState) => {
    // This could be used to redirect the user to a specific page after login.
    // For now, we'll let Auth0 handle the redirect back to the page they were on.
  };

  return (
    <AuthContext.Provider value={auth0}>
      {children}
    </AuthContext.Provider>
  );
};
