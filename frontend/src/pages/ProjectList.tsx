import React, { useState, useEffect } from 'react';
import useApi from '../services/api'; // Assuming you have a custom hook for the api
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper, 
  Button, 
  TextField,
  CircularProgress,
  Divider,
  Alert,
  Snackbar,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Tooltip,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import ForestIcon from '@mui/icons-material/Forest';
import VisibilityIcon from '@mui/icons-material/Visibility';

// Define Project type
interface Project {
  id: string;
  name: string;
  description: string;
  project_type: string;
  status: string;
}

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  const api = useApi();
  
  useEffect(() => {
    const fetchProjects = async () => {
      if (!api) return;
      try {
        setLoading(true);
        const response = await api.get('/projects/');
        setProjects(response.data);
      } catch (err) {
        setError('Failed to fetch projects.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [api]);

  // Function to handle project deletion
  const handleDeleteProject = async () => {
    if (!projectToDelete) return;
    
    try {
      // In a real implementation, this would use the projectService
      // await projectService.deleteProject(projectToDelete.id);
      
      // For now, just update the local state
      setProjects(projects.filter(project => project.id !== projectToDelete.id));
      
      setSnackbarMessage(`Project "${projectToDelete.name}" deleted successfully`);
      setSnackbarOpen(true);
    } catch (err) {
      console.error('Error deleting project:', err);
      setSnackbarMessage('Failed to delete project. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setDeleteDialogOpen(false);
      setProjectToDelete(null);
    }
  };

  // Function to open delete confirmation dialog
  const openDeleteDialog = (project: Project) => {
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  };

  // Filter projects based on search term
  const filteredProjects = projects.filter(project => 
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.project_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Projects
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            component={Link}
            to="/projects/new"
          >
            New Project
          </Button>
        </Box>

        <Paper sx={{ p: 3, mb: 4 }}>
          <TextField
            fullWidth
            label="Search Projects"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by name, description, or project type"
            sx={{ mb: 2 }}
          />
          
          <Divider sx={{ my: 2 }} />
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          ) : filteredProjects.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No projects found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {searchTerm ? 'Try adjusting your search criteria' : 'Create your first project to get started'}
              </Typography>
              {!searchTerm && (
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  component={Link}
                  to="/projects/new"
                  sx={{ mt: 2 }}
                >
                  Create Project
                </Button>
              )}
            </Box>
          ) : (
            <List>
              {filteredProjects.map((project) => (
                <ListItem
                  key={project.id}
                  button
                  component={Link}
                  to={`/projects/${project.id}`}
                >
                  <ListItemText
                    primary={project.name}
                    secondary={`${project.project_type} - ${project.status}`}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Paper>
      </Box>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the project "{projectToDelete?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteProject} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default ProjectList;
