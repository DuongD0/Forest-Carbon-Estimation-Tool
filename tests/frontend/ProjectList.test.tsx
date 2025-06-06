import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProjectList from '../src/pages/ProjectList';

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  Link: ({ children, to }) => <a href={to}>{children}</a>
}));

// Test suite for ProjectList component
describe('ProjectList Component', () => {
  const renderProjectListComponent = () => {
    return render(
      <BrowserRouter>
        <ProjectList />
      </BrowserRouter>
    );
  };

  test('renders project list with header and new project button', async () => {
    renderProjectListComponent();
    
    // Wait for the component to load data
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // Check for heading and new project button
    expect(screen.getByText('Projects')).toBeInTheDocument();
    const newProjectButton = screen.getByText('New Project');
    expect(newProjectButton).toBeInTheDocument();
    expect(newProjectButton.closest('a')).toHaveAttribute('href', '/projects/new');
    
    // Check for search field
    expect(screen.getByLabelText('Search Projects')).toBeInTheDocument();
  });

  test('displays project cards with correct information', async () => {
    renderProjectListComponent();
    
    // Wait for the component to load data
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // Check for project names
    expect(screen.getByText('Amazon Rainforest Conservation')).toBeInTheDocument();
    expect(screen.getByText('Borneo Mangrove Restoration')).toBeInTheDocument();
    expect(screen.getByText('Congo Basin Forest Protection')).toBeInTheDocument();
    
    // Check for project details
    expect(screen.getByText('Brazil')).toBeInTheDocument();
    expect(screen.getByText('Indonesia')).toBeInTheDocument();
    expect(screen.getByText('Democratic Republic of Congo')).toBeInTheDocument();
    
    // Check for view details links
    const viewDetailsLinks = screen.getAllByText('View Details');
    expect(viewDetailsLinks.length).toBe(3);
    expect(viewDetailsLinks[0].closest('a')).toHaveAttribute('href', '/projects/1');
  });

  test('search functionality filters projects correctly', async () => {
    renderProjectListComponent();
    
    // Wait for the component to load data
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // Initially all projects should be visible
    expect(screen.getByText('Amazon Rainforest Conservation')).toBeInTheDocument();
    expect(screen.getByText('Borneo Mangrove Restoration')).toBeInTheDocument();
    expect(screen.getByText('Congo Basin Forest Protection')).toBeInTheDocument();
    
    // Search for "Amazon"
    const searchInput = screen.getByLabelText('Search Projects');
    fireEvent.change(searchInput, { target: { value: 'Amazon' } });
    
    // Only Amazon project should be visible
    expect(screen.getByText('Amazon Rainforest Conservation')).toBeInTheDocument();
    expect(screen.queryByText('Borneo Mangrove Restoration')).not.toBeInTheDocument();
    expect(screen.queryByText('Congo Basin Forest Protection')).not.toBeInTheDocument();
    
    // Clear search
    fireEvent.change(searchInput, { target: { value: '' } });
    
    // All projects should be visible again
    expect(screen.getByText('Amazon Rainforest Conservation')).toBeInTheDocument();
    expect(screen.getByText('Borneo Mangrove Restoration')).toBeInTheDocument();
    expect(screen.getByText('Congo Basin Forest Protection')).toBeInTheDocument();
  });

  test('delete confirmation dialog works correctly', async () => {
    renderProjectListComponent();
    
    // Wait for the component to load data
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // Find delete buttons (they have DeleteIcon)
    const deleteButtons = screen.getAllByRole('button', { name: '' });
    
    // Click the first delete button
    fireEvent.click(deleteButtons[1]); // The second button in each card is the delete button
    
    // Check that confirmation dialog appears
    expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to delete the project/)).toBeInTheDocument();
    
    // Find cancel and delete buttons in dialog
    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    const confirmDeleteButton = screen.getByRole('button', { name: 'Delete' });
    
    // Click cancel
    fireEvent.click(cancelButton);
    
    // Dialog should disappear
    await waitFor(() => {
      expect(screen.queryByText('Confirm Deletion')).not.toBeInTheDocument();
    });
    
    // All projects should still be visible
    expect(screen.getByText('Amazon Rainforest Conservation')).toBeInTheDocument();
    expect(screen.getByText('Borneo Mangrove Restoration')).toBeInTheDocument();
    expect(screen.getByText('Congo Basin Forest Protection')).toBeInTheDocument();
  });
});
