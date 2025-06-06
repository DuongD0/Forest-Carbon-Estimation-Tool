import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../src/pages/Dashboard';
import { AuthProvider } from '../src/contexts/AuthContext';

// Mock the components that are used in Dashboard
jest.mock('../src/components/dashboard/StatCard', () => {
  return function MockStatCard({ title, value, icon, color }) {
    return (
      <div data-testid="stat-card">
        <div data-testid="stat-title">{title}</div>
        <div data-testid="stat-value">{value}</div>
      </div>
    );
  };
});

jest.mock('../src/components/dashboard/RecentProjects', () => {
  return function MockRecentProjects() {
    return <div data-testid="recent-projects">Recent Projects Mock</div>;
  };
});

jest.mock('../src/components/dashboard/RecentForests', () => {
  return function MockRecentForests() {
    return <div data-testid="recent-forests">Recent Forests Mock</div>;
  };
});

jest.mock('../src/components/dashboard/CarbonSummary', () => {
  return function MockCarbonSummary() {
    return <div data-testid="carbon-summary">Carbon Summary Mock</div>;
  };
});

// Mock the useAuth hook
jest.mock('../src/contexts/AuthContext', () => {
  const originalModule = jest.requireActual('../src/contexts/AuthContext');
  return {
    ...originalModule,
    useAuth: () => ({
      user: { name: 'Test User', email: 'test@example.com' }
    })
  };
});

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  Link: ({ children, to }) => <a href={to}>{children}</a>
}));

// Test suite for Dashboard component
describe('Dashboard Component', () => {
  const renderDashboardComponent = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  test('renders dashboard with all sections', () => {
    renderDashboardComponent();
    
    // Check for heading
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText(/Welcome back, Test User/i)).toBeInTheDocument();
    
    // Check for stat cards
    const statCards = screen.getAllByTestId('stat-card');
    expect(statCards.length).toBe(4);
    
    // Check for quick actions section
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('New Project')).toBeInTheDocument();
    expect(screen.getByText('Add Forest')).toBeInTheDocument();
    expect(screen.getByText('Upload Imagery')).toBeInTheDocument();
    expect(screen.getByText('Calculate Carbon')).toBeInTheDocument();
    
    // Check for recent activity and summaries
    expect(screen.getByTestId('recent-projects')).toBeInTheDocument();
    expect(screen.getByTestId('recent-forests')).toBeInTheDocument();
    expect(screen.getByTestId('carbon-summary')).toBeInTheDocument();
  });

  test('quick action buttons have correct links', () => {
    renderDashboardComponent();
    
    // Check that the quick action buttons link to the correct routes
    const newProjectButton = screen.getByText('New Project').closest('a');
    const addForestButton = screen.getByText('Add Forest').closest('a');
    const uploadImageryButton = screen.getByText('Upload Imagery').closest('a');
    const calculateCarbonButton = screen.getByText('Calculate Carbon').closest('a');
    
    expect(newProjectButton).toHaveAttribute('href', '/projects/new');
    expect(addForestButton).toHaveAttribute('href', '/forests/new');
    expect(uploadImageryButton).toHaveAttribute('href', '/imageries/upload');
    expect(calculateCarbonButton).toHaveAttribute('href', '/carbon-calculation');
  });

  test('stat cards display correct information', () => {
    renderDashboardComponent();
    
    // Get all stat titles and values
    const statTitles = screen.getAllByTestId('stat-title');
    const statValues = screen.getAllByTestId('stat-value');
    
    // Check that we have the expected stat cards
    expect(statTitles[0].textContent).toBe('Total Projects');
    expect(statTitles[1].textContent).toBe('Forest Areas');
    expect(statTitles[2].textContent).toBe('Imagery Sets');
    expect(statTitles[3].textContent).toBe('Carbon Credits');
    
    // Check the values
    expect(statValues[0].textContent).toBe('5');
    expect(statValues[1].textContent).toBe('12');
    expect(statValues[2].textContent).toBe('24');
    expect(statValues[3].textContent).toBe('1,250');
  });
});
