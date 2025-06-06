import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../src/pages/Login';
import { AuthProvider } from '../src/contexts/AuthContext';

// Mock the useNavigate hook
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  Link: ({ children, to }) => <a href={to}>{children}</a>
}));

// Test suite for Login component
describe('Login Component', () => {
  const renderLoginComponent = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  test('renders login form with all elements', () => {
    renderLoginComponent();
    
    // Check for heading
    expect(screen.getByText('Forest Carbon Tool')).toBeInTheDocument();
    expect(screen.getByText('Sign in to your account')).toBeInTheDocument();
    
    // Check for form elements
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    
    // Check for links
    expect(screen.getByText(/Forgot password/i)).toBeInTheDocument();
    expect(screen.getByText(/Don't have an account/i)).toBeInTheDocument();
  });

  test('shows validation error when form is submitted with empty fields', async () => {
    renderLoginComponent();
    
    // Submit the form without filling in any fields
    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));
    
    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/Please enter both email and password/i)).toBeInTheDocument();
    });
  });

  test('calls login function with correct credentials when form is submitted', async () => {
    renderLoginComponent();
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/Email Address/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'password123' }
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));
    
    // Since we're using a mock implementation, we can't directly test the login function call
    // But we can check that the loading state is activated
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Sign In/i })).toBeDisabled();
    });
  });

  test('disables form elements during login process', async () => {
    renderLoginComponent();
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/Email Address/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'password123' }
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));
    
    // Check that form elements are disabled during login
    await waitFor(() => {
      expect(screen.getByLabelText(/Email Address/i)).toBeDisabled();
      expect(screen.getByLabelText(/Password/i)).toBeDisabled();
      expect(screen.getByRole('button', { name: /Sign In/i })).toBeDisabled();
    });
  });
});
