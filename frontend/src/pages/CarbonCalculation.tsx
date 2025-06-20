import React, { useState, useEffect, useMemo } from 'react';
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
  StepContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { projectService, calculationService } from '../services/api';
import { Project } from '../types';
import ForestImageryUpload, { ImageryMetadata } from '../components/ForestImageryUpload';
import ImageUpload from '../components/ImageUpload';
import ForestAnalysisVisualization from '../components/ForestAnalysisVisualization';

interface CalculationState {
  selectedImagery: ImageryMetadata | null;
  selectedProject: Project | null;
  calculating: boolean;
  result: any | null;
  error: string | null;
  showVisualization: boolean;
  showForestTypeDialog: boolean;
  selectedForestType: string | null;
}

// hey define the forest types available in Vietnam
const VIETNAMESE_FOREST_TYPES = [
  { value: 'mangrove', label: 'Mangrove Forest', description: 'Coastal wetland forests, high carbon storage' },
  { value: 'evergreen_broadleaf', label: 'Evergreen Broadleaf Forest', description: 'Dense tropical rainforest' },
  { value: 'deciduous_dipterocarp', label: 'Deciduous Dipterocarp Forest', description: 'Seasonal dry forest' },
  { value: 'bamboo_forest', label: 'Bamboo Forest', description: 'Fast-growing bamboo stands' },
  { value: 'melaleuca', label: 'Melaleuca Forest', description: 'Wetland forest, paper bark trees' },
  { value: 'planted_acacia', label: 'Planted Acacia Forest', description: 'Commercial timber plantation' },
  { value: 'mixed', label: 'Mixed Forest Types', description: 'Let system detect automatically' },
];

const CarbonCalculation: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsError, setProjectsError] = useState<string | null>(null);
  const [projectsLoading, setProjectsLoading] = useState(true);
  
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [calculationResult, setCalculationResult] = useState<any | null>(null);
  const [calculationError, setCalculationError] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  
  // New state for image upload workflow
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [imageMetadata, setImageMetadata] = useState<ImageryMetadata[]>([]);
  const [calculationMethod, setCalculationMethod] = useState<'project' | 'image'>('project');

  const [state, setState] = useState<CalculationState>({
    selectedImagery: null,
    selectedProject: null,
    calculating: false,
    result: null,
    error: null,
    showVisualization: false,
    showForestTypeDialog: false,
    selectedForestType: null,
  });

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
            ecosystem_type: 'automatic', // Let the system detect automatically
            scale_factor: imageMetadata[0].resolution || 1.0 // Use resolution from metadata
          };
          
          const calculationResponse = await calculationService.calculateArea(
            uploadedImages[0], 
            calculationParams
          );
          
          // Check if we have the new automatic detection response format
          if (calculationResponse.forest_regions && calculationResponse.visualization) {
            // New automatic detection format
            result = calculationResponse;
          } else {
            // Legacy format - calculate carbon credits
            const creditResponse = await calculationService.calculateCredits({
              area_ha: calculationResponse.area_hectares || calculationResponse.area_ha || 100,
              ecosystem_type: 'vietnamese_forest',
              region: 'vietnam',
              years: 1,
              leakage_factor: 0.0,
              uncertainty_factor: 0.15,
              buffer_percent: 0.15
            });
            
            result = {
              legacy: true,
              credits: creditResponse.creditable_carbon_credits_tCO2e || creditResponse.total_carbon_stock || 0,
              area: calculationResponse.area_hectares || calculationResponse.area_ha || 100
            };
          }
        } else {
          throw new Error('No images available for calculation');
        }
      }
      
      setCalculationResult(result);
      setActiveStep(2);
    } catch (error) {
      setCalculationError('Failed to calculate carbon. Please try again.');
      console.error('Error calculating carbon:', error);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleCalculate = async () => {
    console.log('handleCalculate called');
    console.log('uploadedImages:', uploadedImages);
    console.log('imageMetadata:', imageMetadata);
    
    // hey, we need to use the uploaded images and metadata from the main component state
    if (uploadedImages.length === 0 || imageMetadata.length === 0) {
      console.log('No images uploaded, setting error');
      setCalculationError('Please upload at least one image first.');
      return;
    }

    console.log('Setting state to show forest type dialog');
    // Set the selected imagery and project in the state
    setState(prev => ({ 
      ...prev, 
      selectedImagery: imageMetadata[0],
      selectedProject: projects.find(p => p.id === selectedProjectId) || null,
      showForestTypeDialog: true 
    }));
  };

  const handleForestTypeConfirm = async () => {
    if (uploadedImages.length === 0 || imageMetadata.length === 0) {
      return;
    }

    setState(prev => ({ 
      ...prev, 
      calculating: true, 
      error: null,
      showForestTypeDialog: false 
    }));
    setIsCalculating(true);
    setCalculationError(null);

    try {
      // hey, use the existing calculateArea endpoint with form data that includes forest type
      const response = await calculationService.calculateArea(
        uploadedImages[0],
        {
          metadata: imageMetadata[0],
          analysisType: 'forest_carbon',
          ecosystem_type: 'tropical_forest',
          scale_factor: imageMetadata[0]?.resolution || 1.0,
          forest_type: state.selectedForestType === 'mixed' ? null : state.selectedForestType
        }
      );

      // Check if we got the new format response
      if (response.visualization && (response.total_area_ha !== undefined || response.total_forest_area_ha !== undefined)) {
        // New format with visualization
        setState(prev => ({ 
          ...prev, 
          result: response,
          calculating: false 
        }));
        setCalculationResult(response);
        setActiveStep(2);
      } else if (response.area_hectares || response.area_ha) {
        // Legacy format - calculate carbon credits
        const creditResponse = await calculationService.calculateCredits({
          area_ha: response.area_hectares || response.area_ha || 100,
          ecosystem_type: 'vietnamese_forest',
          region: 'vietnam',
          years: 1,
          leakage_factor: 0.0,
          uncertainty_factor: 0.15,
          buffer_percent: 0.15
        });
        
        const result = {
          legacy: true,
          credits: creditResponse.creditable_carbon_credits_tCO2e || creditResponse.total_carbon_stock || 0,
          area: response.area_hectares || response.area_ha || 100
        };
        
        setState(prev => ({ 
          ...prev, 
          result: result,
          calculating: false 
        }));
        setCalculationResult(result);
        setActiveStep(2);
      } else {
        // Unexpected format
        throw new Error('Unexpected response format from calculation');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to calculate carbon credits';
      setState(prev => ({ 
        ...prev, 
        error: errorMsg,
        calculating: false 
      }));
      setCalculationError(errorMsg);
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Carbon Calculation
      </Typography>
      
      <Box sx={{ width: '100%' }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {/* Step 0: Choose Calculation Method */}
          <Step>
            <StepLabel
              optional={
                activeStep > 0 && (
                  <Typography variant="caption">
                    {calculationMethod === 'project' ? 'Project-Based' : 'Image-Based'}
                  </Typography>
                )
              }
            >
              Choose Calculation Method
            </StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary" paragraph>
                Select whether you want to calculate carbon based on an existing project or by uploading new imagery.
              </Typography>
              
              <Grid container spacing={2}>
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
                        Calculate carbon for an existing project in your account.
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
                        The system will automatically detect forest types and calculate carbon content.
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
            <StepLabel
              optional={
                activeStep > 1 && (
                  <Typography variant="caption">
                    {calculationMethod === 'project' 
                      ? (selectedProjectId ? 'Project selected' : 'No project')
                      : `${uploadedImages.length} image(s) uploaded`}
                  </Typography>
                )
              }
            >
              {calculationMethod === 'project' ? 'Select Project' : 'Upload Forest Imagery'}
            </StepLabel>
            <StepContent>
              {calculationMethod === 'project' ? (
                <Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Select a project from your account to calculate its carbon credits.
                  </Typography>
                  
                  {projectsLoading ? (
                    <CircularProgress />
                  ) : projectsError ? (
                    <Alert severity="error">{projectsError}</Alert>
                  ) : (
                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <InputLabel>Select a Project</InputLabel>
                      <Select
                        value={selectedProjectId}
                        label="Select a Project"
                        onChange={handleProjectChange}
                      >
                        {projects.map((project) => (
                          <MenuItem key={project.id} value={project.id}>
                            {project.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                  
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
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>Automatic Detection Enabled:</strong> Our AI will automatically:
                      <ul style={{ margin: '8px 0' }}>
                        <li>Identify the type of imagery (RGB, false color, NDVI, etc.)</li>
                        <li>Detect Vietnamese forest types (evergreen, mangrove, bamboo, etc.)</li>
                        <li>Generate bounding boxes around forest regions</li>
                        <li>Calculate carbon density for each detected region</li>
                      </ul>
                    </Typography>
                  </Alert>
                  
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
            <StepLabel>
              Calculate Carbon Credits
            </StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary" paragraph>
                Click the button below to run the carbon calculation based on your selection.
                {calculationMethod === 'image' && ' The system will automatically analyze your imagery and detect forest regions.'}
              </Typography>
              
              {calculationError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {calculationError}
                </Alert>
              )}
              
              {!calculationResult && (
                <Box>
                  <Button onClick={() => setActiveStep(1)} sx={{ mr: 1 }}>
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={isCalculating ? <CircularProgress size={20} /> : <CalculateIcon />}
                    onClick={() => {
                      console.log('Calculate button clicked');
                      console.log('Calculation method:', calculationMethod);
                      console.log('Uploaded images:', uploadedImages.length);
                      console.log('Image metadata:', imageMetadata);
                      if (calculationMethod === 'project') {
                        handleCalculateCarbon();
                      } else {
                        handleCalculate();
                      }
                    }}
                    disabled={isCalculating}
                  >
                    {isCalculating ? 'Analyzing...' : 'Calculate Carbon'}
                  </Button>
                </Box>
              )}
              
              {calculationResult && calculationMethod === 'image' && !calculationResult.legacy && (
                <ForestAnalysisVisualization 
                  analysisResult={calculationResult}
                  projectName={uploadedImages[0]?.name}
                  onClose={() => {
                    setCalculationResult(null);
                    setActiveStep(0);
                    setUploadedImages([]);
                    setImageMetadata([]);
                  }}
                />
              )}
              
              {calculationResult && (calculationMethod === 'project' || calculationResult.legacy) && (
                <Paper sx={{ p: 3, mt: 2, backgroundColor: '#f5f5f5' }}>
                  <Typography variant="h6" gutterBottom>
                    Calculation Result
                  </Typography>
                  <Typography variant="h4" color="primary" gutterBottom>
                    {typeof calculationResult === 'number' 
                      ? calculationResult.toFixed(2)
                      : calculationResult.credits?.toFixed(2) || '0'} tCO₂e
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Carbon Credits
                  </Typography>
                  {calculationResult.area && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Forest Area: {calculationResult.area.toFixed(2)} hectares
                    </Typography>
                  )}
                  
                  <Box sx={{ mt: 3 }}>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setCalculationResult(null);
                        setActiveStep(0);
                      }}
                    >
                      Calculate Another
                    </Button>
                  </Box>
                </Paper>
              )}
            </StepContent>
          </Step>
        </Stepper>
      </Box>

      {/* Forest Type Selection Dialog */}
      <Dialog 
        open={state.showForestTypeDialog} 
        onClose={() => setState(prev => ({ ...prev, showForestTypeDialog: false }))}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Select Forest Type</DialogTitle>
        <DialogContent>
          <FormLabel component="legend">Forest Type</FormLabel>
          <RadioGroup
            value={state.selectedForestType || 'mixed'}
            onChange={(e) => setState(prev => ({ ...prev, selectedForestType: e.target.value }))}
          >
            {VIETNAMESE_FOREST_TYPES.map((type) => (
              <FormControlLabel
                key={type.value}
                value={type.value}
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">{type.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {type.description}
                    </Typography>
                  </Box>
                }
                sx={{ mb: 1 }}
              />
            ))}
          </RadioGroup>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setState(prev => ({ ...prev, showForestTypeDialog: false }))}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleForestTypeConfirm} 
            variant="contained"
            disabled={!state.selectedForestType}
          >
            Calculate
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CarbonCalculation;
