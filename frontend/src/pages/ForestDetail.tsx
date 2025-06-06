import React, { useState, useEffect, useCallback } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper, 
  Button, 
  CircularProgress,
  Divider,
  Alert,
  Card,
  CardContent,
  CardActions,
  Select,
  MenuItem,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  FormControl,
  InputLabel,
  Snackbar
} from '@mui/material';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowBack as ArrowBackIcon,
  Calculate as CalculateIcon,
  Image as ImageIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { projectService } from '../services/api';

// Define Forest type
interface Forest {
  id: number;
  project_id: number;
  name: string;
  forest_type: string;
  area_ha: number;
  status: string;
  created_at: string;
  updated_at: string;
  geometry?: any; // GeoJSON for forest boundary
  carbon_stock?: number;
  carbon_credits?: number;
}

// Define Imagery type
interface Imagery {
  id: number;
  forest_id: number;
  name: string;
  acquisition_date: string;
  sensor_type: string;
  status: string;
  created_at: string;
}

const ForestDetail: React.FC = () => {
  const { forestId } = useParams<{ forestId: string }>();
  const navigate = useNavigate();
  
  const [forest, setForest] = useState<Forest | null>(null);
  const [imagery, setImagery] = useState<Imagery[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [calculationDialogOpen, setCalculationDialogOpen] = useState<boolean>(false);
  const [calculationLoading, setCalculationLoading] = useState<boolean>(false);
  const [calculationMethod, setCalculationMethod] = useState<string>('standard');
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  
  const fetchForestData = useCallback(async () => {
    if (!forestId) return;
    try {
      setLoading(true);
      setError(null);
      // Mock data for now, replace with actual API calls
      const mockForest: Forest = {
        id: parseInt(forestId),
        project_id: 1,
        name: 'Cuc Phuong National Park',
        forest_type: 'Tropical Evergreen',
        area_ha: 22200,
        status: 'Active',
        created_at: '2022-01-15T09:00:00Z',
        updated_at: '2023-05-20T14:30:00Z',
        carbon_stock: 1250000,
        carbon_credits: 75000
      };
      const mockImagery: Imagery[] = [
        { id: 1, forest_id: parseInt(forestId), name: 'Landsat 8 - 2023-Q2', acquisition_date: '2023-04-10', sensor_type: 'Landsat 8', status: 'Processed', created_at: '2023-04-12' },
        { id: 2, forest_id: parseInt(forestId), name: 'Sentinel-2 - 2023-Q1', acquisition_date: '2023-02-20', sensor_type: 'Sentinel-2', status: 'Processed', created_at: '2023-02-22' }
      ];
      setForest(mockForest);
      setImagery(mockImagery);
    } catch (err) {
      console.error('Error fetching forest data:', err);
      setError('Failed to fetch forest data. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [forestId]);
  
  useEffect(() => {
    fetchForestData();
  }, [fetchForestData]);
  
  // Function to handle forest deletion
  const handleDeleteForest = async () => {
    // This is a placeholder, in a real app this would call an API
    setSnackbarMessage('Delete functionality not implemented in this demo.');
    setSnackbarOpen(true);
    setDeleteDialogOpen(false);
  };
  
  // Function to handle carbon calculation
  const handleCalculateCarbon = async () => {
    if (!forestId) return;
    try {
      setCalculationLoading(true);
      await projectService.calculateCarbon(parseInt(forestId));
      setSnackbarMessage('Carbon calculation started successfully.');
      setSnackbarOpen(true);
      // You might want to refresh data or show a success message
    } catch(err) {
      setSnackbarMessage('Failed to start carbon calculation.');
      setSnackbarOpen(true);
    } finally {
      setCalculationLoading(false);
      setCalculationDialogOpen(false);
    }
  };
  
  // Function to handle calculation method change
  const handleMethodChange = (event: SelectChangeEvent) => {
    setCalculationMethod(event.target.value);
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (error || !forest) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error || 'Forest not found'}
        </Alert>
        <Button 
          component={Link} 
          to="/forests" 
          variant="contained" 
          sx={{ mt: 2 }}
        >
          Back to Forests
        </Button>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        {/* Forest Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {forest.name}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              {forest.forest_type.replace('_', ' ')} • {forest.area_ha.toLocaleString()} hectares
            </Typography>
          </Box>
          <Box>
            <Button
              variant="outlined"
              color="primary"
              component={Link}
              to={`/forests/${forest.id}/edit`}
              startIcon={<ArrowBackIcon />}
              sx={{ mr: 1 }}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Delete
            </Button>
          </Box>
        </Box>
        
        {/* Forest Details */}
        <Grid container spacing={4}>
          {/* Left Column - Details */}
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Forest Details
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Project
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    <Link to={`/projects/${forest.project_id}`}>
                      View Project
                    </Link>
                  </Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2" sx={{ 
                    color: forest.status === 'active' ? 'success.main' : 
                           forest.status === 'planning' ? 'info.main' : 'text.primary'
                  }}>
                    {forest.status.charAt(0).toUpperCase() + forest.status.slice(1)}
                  </Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Forest Type
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    {forest.forest_type.replace('_', ' ')}
                  </Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Area
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    {forest.area_ha.toLocaleString()} hectares
                  </Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Created
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    {new Date(forest.created_at).toLocaleDateString()}
                  </Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Last Updated
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography variant="body2">
                    {new Date(forest.updated_at).toLocaleDateString()}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
            
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Carbon Data
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {forest.carbon_stock ? (
                <>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Card sx={{ height: '100%' }}>
                        <CardContent>
                          <Typography variant="h3" align="center" color="primary">
                            {forest.carbon_stock?.toLocaleString() ?? 'N/A'}
                          </Typography>
                          <Typography variant="body2" align="center" color="text.secondary">
                            Carbon Stock (Mg C)
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6}>
                      <Card sx={{ height: '100%' }}>
                        <CardContent>
                          <Typography variant="h3" align="center" color="secondary">
                            {forest.carbon_credits?.toLocaleString() ?? 'N/A'}
                          </Typography>
                          <Typography variant="body2" align="center" color="text.secondary">
                            Potential Credits (Mg CO2e)
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 3, textAlign: 'center' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<CalculateIcon />}
                      onClick={() => setCalculationDialogOpen(true)}
                    >
                      Recalculate Carbon
                    </Button>
                  </Box>
                </>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    No carbon data available yet
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<CalculateIcon />}
                    onClick={() => setCalculationDialogOpen(true)}
                    sx={{ mt: 1 }}
                  >
                    Calculate Carbon
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>
          
          {/* Right Column - Map and Imagery */}
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Forest Location
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {/* Map Component (placeholder) */}
              <Box 
                sx={{ 
                  height: 300, 
                  bgcolor: 'grey.200', 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  borderRadius: 1
                }}
              >
                {/* In a real implementation, this would be a proper map component */}
                <Typography variant="body2" color="text.secondary">
                  Map View (Placeholder)
                </Typography>
              </Box>
            </Paper>
            
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Imagery Data
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  component={Link}
                  to={`/imageries/upload?forest_id=${forest.id}`}
                  startIcon={<ImageIcon />}
                  size="small"
                >
                  Upload New
                </Button>
              </Box>
              <Divider sx={{ mb: 2 }} />
              
              {imagery.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    No imagery data available
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    component={Link}
                    to={`/imageries/upload?forest_id=${forest.id}`}
                    startIcon={<ImageIcon />}
                    sx={{ mt: 1 }}
                  >
                    Upload Imagery
                  </Button>
                </Box>
              ) : (
                <Grid container spacing={2}>
                  {imagery.map((imagery) => (
                    <Grid item xs={12} sm={6} key={imagery.id}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" component="div">
                            {imagery.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {imagery.sensor_type}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                              Date:
                            </Typography>
                            <Typography variant="body2">
                              {new Date(imagery.acquisition_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              Status:
                            </Typography>
                            <Typography variant="body2" sx={{ 
                              color: imagery.status === 'processed' ? 'success.main' : 
                                    imagery.status === 'processing' ? 'info.main' : 'text.primary'
                            }}>
                              {imagery.status.charAt(0).toUpperCase() + imagery.status.slice(1)}
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button 
                            size="small" 
                            component={Link} 
                            to={`/imageries/${imagery.id}`}
                          >
                            View Details
                          </Button>
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the forest "{forest.name}"? This action cannot be undone and will also delete all associated imagery and carbon data.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteForest} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Carbon Calculation Dialog */}
      <Dialog
        open={calculationDialogOpen}
        onClose={() => !calculationLoading && setCalculationDialogOpen(false)}
      >
        <DialogTitle>Calculate Carbon</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Select a calculation method and start the carbon estimation process for this forest area.
          </DialogContentText>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="calculation-method-label">Calculation Method</InputLabel>
            <Select
              labelId="calculation-method-label"
              id="calculation-method"
              value={calculationMethod}
              label="Calculation Method"
              onChange={handleMethodChange}
              disabled={calculationLoading}
            >
              <MenuItem value="standard">Standard (IPCC Guidelines)</MenuItem>
              <MenuItem value="enhanced">Enhanced (with NDVI adjustment)</MenuItem>
              <MenuItem value="detailed">Detailed (with species composition)</MenuItem>
            </Select>
          </FormControl>
          
          {calculationLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <CircularProgress />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setCalculationDialogOpen(false)} 
            disabled={calculationLoading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleCalculateCarbon} 
            color="primary" 
            disabled={calculationLoading}
            autoFocus
          >
            Calculate
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

export default ForestDetail;
