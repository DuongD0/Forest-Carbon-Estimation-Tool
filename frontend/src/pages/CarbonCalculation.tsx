import React, { useState, useEffect } from 'react';
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
  CardContent,
  Grid,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { projectService, calculationService } from '../services/api';
import { Project } from '../types';
import ForestImageryUpload, { ImageryMetadata } from '../components/ForestImageryUpload';
import ImageUpload from '../components/ImageUpload';

const CarbonCalculation: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsError, setProjectsError] = useState<string | null>(null);
  const [projectsLoading, setProjectsLoading] = useState(true);
  
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [calculationResult, setCalculationResult] = useState<number | null>(null);
  const [calculationError, setCalculationError] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  
  // New state for image upload workflow
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [imageMetadata, setImageMetadata] = useState<ImageryMetadata[]>([]);
  const [calculationMethod, setCalculationMethod] = useState<'project' | 'image'>('project');

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await projectService.getProjects();
        setProjects(data);
      } catch (err) {
        setProjectsError('Failed to fetch projects');
        console.error('Error fetching projects:', err);
      } finally {
        setProjectsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const handleProjectChange = (event: SelectChangeEvent<string>) => {
    setSelectedProjectId(event.target.value);
    setCalculationResult(null);
    setCalculationError(null);
  };

  const handleCalculationMethodChange = (method: 'project' | 'image') => {
    setCalculationMethod(method);
    setActiveStep(0);
    setCalculationResult(null);
    setCalculationError(null);
    setUploadedImages([]);
    setImageMetadata([]);
  };

  const handleImagesUploaded = (files: File[], metadata: ImageryMetadata[]) => {
    setUploadedImages(files);
    setImageMetadata(metadata);
    setActiveStep(1);
  };

  const handleCalculateCarbon = async () => {
    if (calculationMethod === 'project' && !selectedProjectId) {
      setCalculationError('Please select a project first.');
      return;
    }
    
    if (calculationMethod === 'image' && uploadedImages.length === 0) {
      setCalculationError('Please upload at least one image first.');
      return;
    }
    
    setIsCalculating(true);
    setCalculationError(null);
    setCalculationResult(null);

    try {
      let result;
      
      if (calculationMethod === 'project') {
        // Project-based calculation (existing functionality)
        const mockResult = Math.random() * 1000 + 500; // Random value between 500-1500
        result = mockResult;
      } else {
        // Image-based calculation with uploaded imagery
        if (uploadedImages.length > 0) {
          // Use the first image for calculation (in a real app, you might process all images)
          const calculationParams = {
            metadata: imageMetadata[0],
            analysisType: 'forest_carbon',
            ecosystem_type: 'tropical_forest', // This could be selected by user
            scale_factor: 1.0 // Default scale factor
          };
          
          const calculationResponse = await calculationService.calculateArea(
            uploadedImages[0], 
            calculationParams
          );
          
          // Then calculate carbon credits based on the area
          const creditResponse = await calculationService.calculateCredits({
            area_ha: calculationResponse.area_hectares || calculationResponse.area_ha || 100, // Use available field or default
            ecosystem_type: calculationParams.ecosystem_type,
            region: 'vietnam',
            years: 1,
            leakage_factor: 0.0,
            uncertainty_factor: 0.15,
            buffer_percent: 0.15
          });
          
          result = creditResponse.creditable_carbon_credits_tCO2e || creditResponse.total_carbon_stock || 0;
        } else {
          throw new Error('No images available for calculation');
        }
      }
      
      setCalculationResult(result);
      setActiveStep(2);
    } catch (err: any) {
      // Handle validation errors from backend which return an array of error objects
      let errorMessage = 'An error occurred during calculation.';
      
      if (err.response?.data?.detail) {
        // If detail is an array of validation errors
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail
            .map((error: any) => error.msg || error.message || JSON.stringify(error))
            .join(', ');
        } else if (typeof err.response.data.detail === 'object') {
          // If detail is a single error object
          errorMessage = err.response.data.detail.msg || 
                        err.response.data.detail.message || 
                        JSON.stringify(err.response.data.detail);
        } else {
          // If detail is a string
          errorMessage = err.response.data.detail;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setCalculationError(errorMessage);
      console.error('Calculation error:', err);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    setCalculationResult(null);
    setCalculationError(null);
    setUploadedImages([]);
    setImageMetadata([]);
    setSelectedProjectId('');
  };

  const steps = [
    'Choose Calculation Method',
    calculationMethod === 'project' ? 'Select Project' : 'Upload Images',
    'Run Calculation',
    'View Results'
  ];

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Carbon Stock Calculation
        </Typography>
        <Typography paragraph>
          Calculate carbon stock using either existing project data or by uploading new forest imagery for analysis.
        </Typography>

        <Stepper activeStep={activeStep} orientation="vertical" sx={{ mt: 3 }}>
          {/* Step 0: Choose Method */}
          <Step>
            <StepLabel>Choose Calculation Method</StepLabel>
            <StepContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: calculationMethod === 'project' ? 2 : 1,
                      borderColor: calculationMethod === 'project' ? 'primary.main' : 'divider'
                    }}
                    onClick={() => handleCalculationMethodChange('project')}
                  >
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={2}>
                        <CalculateIcon color="primary" sx={{ mr: 2 }} />
                        <Typography variant="h6">Project-Based</Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Calculate carbon stock for an existing project using predefined ecosystem parameters and area data.
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: calculationMethod === 'image' ? 2 : 1,
                      borderColor: calculationMethod === 'image' ? 'primary.main' : 'divider'
                    }}
                    onClick={() => handleCalculationMethodChange('image')}
                  >
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={2}>
                        <CloudUploadIcon color="primary" sx={{ mr: 2 }} />
                        <Typography variant="h6">Image-Based</Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Upload satellite imagery or aerial photos to analyze forest area and calculate carbon stock.
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  onClick={() => setActiveStep(1)}
                  disabled={!calculationMethod}
                >
                  Continue
                </Button>
              </Box>
            </StepContent>
          </Step>

          {/* Step 1: Project Selection or Image Upload */}
          <Step>
            <StepLabel>
              {calculationMethod === 'project' ? 'Select Project' : 'Upload Images'}
            </StepLabel>
            <StepContent>
              {calculationMethod === 'project' ? (
                <Box>
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
                  
                  <Box sx={{ mt: 2 }}>
                    <Button onClick={() => setActiveStep(0)} sx={{ mr: 1 }}>
                      Back
                    </Button>
                    <Button
                      variant="contained"
                      onClick={() => setActiveStep(2)}
                      disabled={!selectedProjectId}
                    >
                      Continue to Calculation
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Box>
                  <ForestImageryUpload
                    onImagesUploaded={handleImagesUploaded}
                    disabled={false}
                  />
                  
                  {uploadedImages.length > 0 && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      {uploadedImages.length} image(s) uploaded successfully with metadata.
                    </Alert>
                  )}
                  
                  <Box sx={{ mt: 2 }}>
                    <Button onClick={() => setActiveStep(0)} sx={{ mr: 1 }}>
                      Back
                    </Button>
                    <Button
                      variant="contained"
                      onClick={() => setActiveStep(2)}
                      disabled={uploadedImages.length === 0}
                    >
                      Continue to Calculation
                    </Button>
                  </Box>
                </Box>
              )}
            </StepContent>
          </Step>

          {/* Step 2: Run Calculation */}
          <Step>
            <StepLabel>Run Calculation</StepLabel>
            <StepContent>
              <Box>
                <Typography variant="body1" gutterBottom>
                  {calculationMethod === 'project' 
                    ? `Ready to calculate carbon stock for project: ${projects.find(p => p.id === selectedProjectId)?.name}`
                    : `Ready to analyze ${uploadedImages.length} uploaded image(s) and calculate carbon stock.`
                  }
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    startIcon={<CalculateIcon />}
                    onClick={handleCalculateCarbon}
                    disabled={isCalculating}
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
                
                <Box sx={{ mt: 2 }}>
                  <Button onClick={() => setActiveStep(1)} sx={{ mr: 1 }}>
                    Back
                  </Button>
                </Box>
              </Box>
            </StepContent>
          </Step>

          {/* Step 3: Results */}
          <Step>
            <StepLabel>View Results</StepLabel>
            <StepContent>
              {calculationResult !== null && (
                <Box>
                  <Card sx={{ mt: 3, backgroundColor: 'success.light', color: 'success.contrastText' }}>
                    <CardContent>
                      <Typography variant="h6" component="h3" gutterBottom>
                        Calculation Complete
                      </Typography>
                      <Typography variant="h3" component="p" sx={{ fontWeight: 'bold', my: 2 }}>
                        {calculationResult.toFixed(2)}
                      </Typography>
                      <Typography variant="h6">
                        Metric Tons of CO2 equivalent (tCO2e)
                      </Typography>
                      
                      <Divider sx={{ my: 2, backgroundColor: 'success.contrastText' }} />
                      
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="body2">
                            <strong>Calculation Method:</strong> {calculationMethod === 'project' ? 'Project-Based' : 'Image Analysis'}
                          </Typography>
                        </Grid>
                        {calculationMethod === 'project' && (
                          <Grid item xs={12} md={6}>
                            <Typography variant="body2">
                              <strong>Project:</strong> {projects.find(p => p.id === selectedProjectId)?.name}
                            </Typography>
                          </Grid>
                        )}
                        {calculationMethod === 'image' && (
                          <>
                            <Grid item xs={12} md={6}>
                              <Typography variant="body2">
                                <strong>Images Analyzed:</strong> {uploadedImages.length}
                              </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                              <Typography variant="body2">
                                <strong>Primary Satellite:</strong> {imageMetadata[0]?.satellite || 'N/A'}
                              </Typography>
                            </Grid>
                          </>
                        )}
                        <Grid item xs={12}>
                          <Typography variant="body2">
                            <strong>Calculated on:</strong> {new Date().toLocaleString()}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                  
                  <Box sx={{ mt: 3 }}>
                    <Button 
                      variant="outlined" 
                      onClick={handleReset}
                      sx={{ mr: 2 }}
                    >
                      Start New Calculation
                    </Button>
                    <Button 
                      variant="contained"
                      onClick={() => {
                        // In a real app, this would export or save the results
                        alert('Export functionality would be implemented here');
                      }}
                    >
                      Export Results
                    </Button>
                  </Box>
                </Box>
              )}
            </StepContent>
          </Step>
        </Stepper>
      </Paper>
    </Container>
  );
};

export default CarbonCalculation;
