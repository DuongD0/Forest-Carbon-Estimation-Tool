import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Button, 
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Card,
  CardContent
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import useApi from '../hooks/useApi';
import { Project } from '../types';

const CarbonCalculation: React.FC = () => {
  const { data: projects, error: projectsError, isLoading: projectsLoading } = useApi<Project[]>('/projects');
  
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [calculationResult, setCalculationResult] = useState<number | null>(null);
  const [calculationError, setCalculationError] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  const { api } = useApi();

  const handleProjectChange = (event: SelectChangeEvent<string>) => {
    setSelectedProjectId(event.target.value);
    setCalculationResult(null);
    setCalculationError(null);
  };

  const handleCalculateCarbon = async () => {
    if (!selectedProjectId) {
      setCalculationError('Please select a project first.');
      return;
    }
    
    setIsCalculating(true);
    setCalculationError(null);
    setCalculationResult(null);

    try {
      const response = await api.post(`/projects/${selectedProjectId}/calculate_carbon`);
      setCalculationResult(response.data);
    } catch (err: any) {
      setCalculationError(err.response?.data?.detail || 'An error occurred during calculation.');
      console.error(err);
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Carbon Stock Calculation
        </Typography>
        <Typography paragraph>
          Select a project to calculate its estimated total carbon stock based on its defined ecosystem and area.
        </Typography>

        <Box sx={{ mt: 3 }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="project-select-label">Select Project</InputLabel>
            <Select
              labelId="project-select-label"
              id="project-select"
              value={selectedProjectId}
              label="Select Project"
              onChange={handleProjectChange}
              disabled={projectsLoading || !projects}
            >
              {projectsLoading && <MenuItem value=""><em>Loading projects...</em></MenuItem>}
              {projectsError && <MenuItem value=""><em>Error loading projects</em></MenuItem>}
              {projects && projects.map((project: Project) => (
                <MenuItem key={project.id} value={project.id}>
                  {project.name} ({project.project_type})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<CalculateIcon />}
              onClick={handleCalculateCarbon}
              disabled={!selectedProjectId || isCalculating}
            >
              {isCalculating ? 'Calculating...' : 'Run Calculation'}
              {isCalculating && <CircularProgress size={24} sx={{ position: 'absolute', top: '50%', left: '50%', marginTop: '-12px', marginLeft: '-12px' }} />}
            </Button>
          </Box>
          
          {calculationError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {calculationError}
            </Alert>
          )}

          {calculationResult !== null && (
            <Card sx={{ mt: 3, backgroundColor: 'grey.100' }}>
              <CardContent>
                <Typography variant="h6" component="h3">Calculation Result</Typography>
                <Typography variant="h4" component="p" sx={{ fontWeight: 'bold', mt: 1 }}>
                  {calculationResult.toFixed(2)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Metric Tons of CO2 equivalent (tCO2e)
                </Typography>
              </CardContent>
            </Card>
          )}

        </Box>
      </Paper>
    </Container>
  );
};

export default CarbonCalculation;
