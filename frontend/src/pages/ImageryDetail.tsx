import React, { useState, useEffect, useCallback } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Tabs,
  Tab,
  Stack,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowBack as ArrowBackIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import { imageryService } from '../services/api';

// Define Imagery type
interface Imagery {
  id: number;
  forest_id: number;
  name: string;
  acquisition_date: string;
  sensor_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  file_path?: string;
  file_format?: string;
  processing_log?: string;
  metadata?: {
    bands?: string[];
    resolution?: number;
    cloud_cover?: number;
    crs?: string;
    [key: string]: any;
  };
}

// Define Processing Result type
interface ProcessingResult {
  id: number;
  imagery_id: number;
  result_type: string;
  file_path: string;
  created_at: string;
  metadata?: any;
}

const ImageryDetail: React.FC = () => {
  const { imageryId } = useParams<{ imageryId: string }>();
  const navigate = useNavigate();
  
  const [imagery, setImagery] = useState<Imagery | null>(null);
  const [processingResults, setProcessingResults] = useState<ProcessingResult[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  
  const fetchImageryData = useCallback(async () => {
    if (!imageryId) return;
    try {
      setLoading(true);
      setError(null);
      const imageryData = await imageryService.getImageryById(parseInt(imageryId));
      setImagery(imageryData);
    } catch (err) {
      console.error('Error fetching imagery data:', err);
      setError('Failed to fetch imagery data. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [imageryId]);

  useEffect(() => {
    fetchImageryData();
  }, [fetchImageryData]);
  
  const handleProcessImagery = async () => {
    if (!imageryId) return;
    try {
      setProcessing(true);
      await imageryService.processImagery(parseInt(imageryId));
      setSnackbarMessage('Imagery processing started successfully.');
      setSnackbarOpen(true);
      // Optionally, refresh data after a delay
      setTimeout(() => fetchImageryData(), 5000);
    } catch (err) {
      console.error('Error processing imagery:', err);
      setSnackbarMessage('Failed to start imagery processing.');
      setSnackbarOpen(true);
    } finally {
      setProcessing(false);
    }
  };
  
  const handleDeleteImagery = async () => {
    if (!imageryId) return;
    if (window.confirm('Are you sure you want to delete this imagery record?')) {
      try {
        await imageryService.deleteImagery(parseInt(imageryId));
        setSnackbarMessage('Imagery record deleted successfully.');
        setSnackbarOpen(true);
        navigate(-1); // Go back to the previous page
      } catch (err) {
        console.error('Error deleting imagery:', err);
        setSnackbarMessage('Failed to delete imagery record.');
        setSnackbarOpen(true);
      }
    }
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
  
  if (error || !imagery) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error || 'Imagery not found'}
        </Alert>
        <Button 
          component={Link} 
          to="/imageries" 
          variant="contained" 
          sx={{ mt: 2 }}
        >
          Back to Imagery List
        </Button>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Imagery: {imagery.name}
        </Typography>
        <Button
          variant="outlined"
          onClick={() => navigate(`/projects/${imagery.forest_id}`)}
        >
          Back to Forest
        </Button>
      </Box>

      <Stack spacing={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Details</Typography>
          <List>
            <ListItem><ListItemText primary="Status" secondary={imagery.status} /></ListItem>
            <ListItem><ListItemText primary="Acquisition Date" secondary={new Date(imagery.acquisition_date).toLocaleString()} /></ListItem>
            <ListItem><ListItemText primary="Sensor" secondary={imagery.sensor_type} /></ListItem>
            <ListItem><ListItemText primary="File Path" secondary={imagery.file_path} /></ListItem>
          </List>
        </Paper>

        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Actions</Typography>
          <Button
            variant="contained"
            color="secondary"
            startIcon={processing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleProcessImagery}
            disabled={processing || imagery.status === 'Processing'}
          >
            {processing ? 'Processing...' : 'Run Processing'}
          </Button>
        </Paper>

        {imagery.processing_log && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Processing Log</Typography>
            <Box component="pre" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', maxHeight: 300, overflowY: 'auto', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
              {imagery.processing_log}
            </Box>
          </Paper>
        )}
      </Stack>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4 }}>
        <Button 
          variant="contained" 
          color="secondary"
          onClick={handleDeleteImagery}
          disabled={processing}
        >
          Delete
        </Button>
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default ImageryDetail;
