import React, { useState, useEffect } from 'react';
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
  Tooltip
} from '@mui/material';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import ForestIcon from '@mui/icons-material/Forest';
import VisibilityIcon from '@mui/icons-material/Visibility';

// Define Project type
interface Project {
  id: number;
  name: string;
  description: string;
  location: string;
  area_ha: number;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  updated_at: string;
  forest_count?: number;
}

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  
  // Fetch projects on component mount
  useEffect(() => {
    fetchProjects();
  }, []);

  // Function to fetch projects from API
  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would use the projectService
      // const data = await projectService.getProjects();
      
      // For now, use mock data
      const mockProjects: Project[] = [
        {
          id: 1,
          name: 'Amazon Rainforest Conservation',
          description: 'Conservation project in the Amazon rainforest focusing on sustainable management and carbon sequestration.',
          location: 'Brazil',
          area_ha: 5000,
          start_date: '2023-01-01',
          end_date: '2028-01-01',
          status: 'active',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
          forest_count: 3
        },
        {
          id: 2,
          name: 'Borneo Mangrove Restoration',
          description: 'Restoration of mangrove forests in Borneo to improve coastal resilience and carbon storage.',
          location: 'Indonesia',
          area_ha: 1200,
          start_date: '2022-06-15',
          end_date: '2027-06-15',
          status: 'active',
          created_at: '2022-06-15T00:00:00Z',
          updated_at: '2022-06-15T00:00:00Z',
          forest_count: 2
        },
        {
          id: 3,
          name: 'Congo Basin Forest Protection',
          description: 'Protection of primary forests in the Congo Basin to preserve biodiversity and carbon stocks.',
          location: 'Democratic Republic of Congo',
          area_ha: 8500,
          start_date: '2023-03-10',
          end_date: '2033-03-10',
          status: 'planning',
          created_at: '2023-03-10T00:00:00Z',
          updated_at: '2023-03-10T00:00:00Z',
          forest_count: 0
        }
      ];
      
      setProjects(mockProjects);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to fetch projects. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

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
    project.location.toLowerCase().includes(searchTerm.toLowerCase())
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
            placeholder="Search by name, description, or location"
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
            <Grid container spacing={3}>
              {filteredProjects.map((project) => (
                <Grid item xs={12} md={6} lg={4} key={project.id}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" component="div" gutterBottom>
                        {project.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {project.description}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Location:
                        </Typography>
                        <Typography variant="body2">
                          {project.location}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Area:
                        </Typography>
                        <Typography variant="body2">
                          {project.area_ha.toLocaleString()} ha
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Status:
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          color: project.status === 'active' ? 'success.main' : 
                                 project.status === 'planning' ? 'info.main' : 'text.primary'
                        }}>
                          {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          Forests:
                        </Typography>
                        <Typography variant="body2">
                          {project.forest_count || 0}
                        </Typography>
                      </Box>
                    </CardContent>
                    <CardActions sx={{ justifyContent: 'space-between', p: 2, pt: 0 }}>
                      <Button 
                        size="small" 
                        component={Link} 
                        to={`/projects/${project.id}`}
                      >
                        View Details
                      </Button>
                      <Box>
                        <IconButton 
                          size="small" 
                          color="primary"
                          component={Link}
                          to={`/projects/${project.id}/edit`}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => openDeleteDialog(project)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
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
