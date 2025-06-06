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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import ForestIcon from '@mui/icons-material/Forest';
import DownloadIcon from '@mui/icons-material/Download';
import { Link, useParams } from 'react-router-dom';

// Define Forest type
interface Forest {
  id: number;
  name: string;
  forest_type: string;
  area_ha: number;
}

// Define Carbon Calculation Result type
interface CarbonResult {
  id: number;
  forest_id: number;
  calculation_date: string;
  method: string;
  carbon_stock: number;
  carbon_credits: number;
  baseline_year: string;
  project_year: string;
  status: string;
  metadata?: any;
}

const CarbonCalculation: React.FC = () => {
  const { forestId } = useParams<{ forestId?: string }>();
  
  const [forests, setForests] = useState<Forest[]>([]);
  const [selectedForestId, setSelectedForestId] = useState<number | null>(forestId ? parseInt(forestId) : null);
  const [calculationMethod, setCalculationMethod] = useState<string>('standard');
  const [baselineYear, setBaselineYear] = useState<string>('2020');
  const [projectYear, setProjectYear] = useState<string>('2023');
  const [calculationResults, setCalculationResults] = useState<CarbonResult[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  
  // Function to fetch forests
  const fetchForests = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would use the forestService
      // const forestsData = projectIdParam 
      //   ? await forestService.getForests(parseInt(projectIdParam))
      //   : await forestService.getForests();
      
      // For now, use mock data
      const mockForests: Forest[] = [
        {
          id: 1,
          name: 'Primary Forest Block A',
          forest_type: 'TROPICAL_EVERGREEN',
          area_ha: 2500
        },
        {
          id: 2,
          name: 'Secondary Growth Area',
          forest_type: 'DECIDUOUS',
          area_ha: 1200
        },
        {
          id: 3,
          name: 'Restoration Zone',
          forest_type: 'OTHER',
          area_ha: 800
        }
      ];
      
      setForests(mockForests);
      
      // If forestId is not provided but we have forests, select the first one
      if (!selectedForestId && mockForests.length > 0) {
        setSelectedForestId(mockForests[0].id);
      }
    } catch (err) {
      console.error('Error fetching forests:', err);
      setError('Failed to fetch forests. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [selectedForestId]);
  
  // Fetch forests and calculation results on component mount
  useEffect(() => {
    fetchForests();
    if (selectedForestId) {
      fetchCalculationResults(selectedForestId);
    }
  }, [selectedForestId, fetchForests]);
  
  // Function to fetch calculation results for a forest
  const fetchCalculationResults = async (forestId: number) => {
    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would use the forestService
      // const resultsData = await forestService.getCarbonCalculationResults(forestId);
      
      // For now, use mock data
      const mockResults: CarbonResult[] = [
        {
          id: 1,
          forest_id: forestId,
          calculation_date: '2023-06-15T10:30:00Z',
          method: 'standard',
          carbon_stock: 450000,
          carbon_credits: 25000,
          baseline_year: '2020',
          project_year: '2023',
          status: 'completed'
        },
        {
          id: 2,
          forest_id: forestId,
          calculation_date: '2023-05-20T14:45:00Z',
          method: 'enhanced',
          carbon_stock: 475000,
          carbon_credits: 28000,
          baseline_year: '2020',
          project_year: '2023',
          status: 'completed'
        }
      ];
      
      setCalculationResults(mockResults);
    } catch (err) {
      console.error('Error fetching calculation results:', err);
      setError('Failed to fetch calculation results. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  // Function to handle forest selection change
  const handleForestChange = (event: SelectChangeEvent) => {
    const forestId = parseInt(event.target.value);
    setSelectedForestId(forestId);
    fetchCalculationResults(forestId);
  };
  
  // Function to handle calculation method change
  const handleMethodChange = (event: SelectChangeEvent) => {
    setCalculationMethod(event.target.value);
  };
  
  // Function to handle baseline year change
  const handleBaselineYearChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setBaselineYear(event.target.value);
  };
  
  // Function to handle project year change
  const handleProjectYearChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setProjectYear(event.target.value);
  };
  
  // Function to handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  // Function to handle carbon calculation
  const handleCalculateCarbon = async () => {
    if (!selectedForestId) {
      setSnackbarMessage('Please select a forest first');
      setSnackbarOpen(true);
      return;
    }
    
    try {
      setCalculating(true);
      
      // In a real implementation, this would use the forestService
      // const result = await forestService.calculateCarbonCredits(selectedForestId, {
      //   method: calculationMethod,
      //   baseline_year: baselineYear,
      //   project_year: projectYear
      // });
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock result
      const mockResult: CarbonResult = {
        id: calculationResults.length + 1,
        forest_id: selectedForestId,
        calculation_date: new Date().toISOString(),
        method: calculationMethod,
        carbon_stock: calculationMethod === 'standard' ? 450000 : calculationMethod === 'enhanced' ? 475000 : 490000,
        carbon_credits: calculationMethod === 'standard' ? 25000 : calculationMethod === 'enhanced' ? 28000 : 32000,
        baseline_year: baselineYear,
        project_year: projectYear,
        status: 'completed'
      };
      
      // Add new result to list
      setCalculationResults([mockResult, ...calculationResults]);
      
      setSnackbarMessage('Carbon calculation completed successfully');
      setSnackbarOpen(true);
      
      // Switch to results tab
      setTabValue(1);
    } catch (err) {
      console.error('Error calculating carbon:', err);
      setSnackbarMessage('Failed to calculate carbon. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setCalculating(false);
    }
  };
  
  // Get the selected forest
  const selectedForest = forests.find(forest => forest.id === selectedForestId);
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Carbon Calculation
        </Typography>
        
        {loading && !calculating ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        ) : (
          <>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Select Forest Area
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="forest-select-label">Forest Area</InputLabel>
                <Select
                  labelId="forest-select-label"
                  id="forest-select"
                  value={selectedForestId?.toString() || ''}
                  label="Forest Area"
                  onChange={handleForestChange}
                >
                  {forests.map((forest) => (
                    <MenuItem key={forest.id} value={forest.id.toString()}>
                      {forest.name} ({forest.area_ha.toLocaleString()} ha)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              {selectedForest && (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {selectedForest.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {selectedForest.forest_type.replace('_', ' ')}
                        </Typography>
                        <Typography variant="h4" color="primary">
                          {selectedForest.area_ha.toLocaleString()} ha
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Button
                        variant="contained"
                        color="primary"
                        component={Link}
                        to={`/forests/${selectedForestId}`}
                        startIcon={<ForestIcon />}
                      >
                        View Forest Details
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              )}
            </Paper>
            
            <Paper sx={{ p: 3 }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="carbon calculation tabs">
                  <Tab label="Calculate" />
                  <Tab label="Results" />
                </Tabs>
              </Box>
              
              {/* Calculate Tab */}
              {tabValue === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Calculation Parameters
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel id="method-select-label">Calculation Method</InputLabel>
                        <Select
                          labelId="method-select-label"
                          id="method-select"
                          value={calculationMethod}
                          label="Calculation Method"
                          onChange={handleMethodChange}
                          disabled={calculating}
                        >
                          <MenuItem value="standard">Standard (IPCC Guidelines)</MenuItem>
                          <MenuItem value="enhanced">Enhanced (with NDVI adjustment)</MenuItem>
                          <MenuItem value="detailed">Detailed (with species composition)</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="Baseline Year"
                        value={baselineYear}
                        onChange={handleBaselineYearChange}
                        disabled={calculating}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="Project Year"
                        value={projectYear}
                        onChange={handleProjectYearChange}
                        disabled={calculating}
                      />
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 4, textAlign: 'center' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      size="large"
                      startIcon={<CalculateIcon />}
                      onClick={handleCalculateCarbon}
                      disabled={calculating || !selectedForestId}
                      sx={{ minWidth: 200 }}
                    >
                      {calculating ? <CircularProgress size={24} /> : 'Calculate Carbon'}
                    </Button>
                  </Box>
                  
                  {calculating && (
                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        Calculating carbon for {selectedForest?.name}...
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
              
              {/* Results Tab */}
              {tabValue === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Calculation Results
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  {calculationResults.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body1" color="text.secondary" gutterBottom>
                        No calculation results available
                      </Typography>
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={() => setTabValue(0)}
                        sx={{ mt: 1 }}
                      >
                        Perform Calculation
                      </Button>
                    </Box>
                  ) : (
                    <>
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Date</TableCell>
                              <TableCell>Method</TableCell>
                              <TableCell>Baseline</TableCell>
                              <TableCell>Project</TableCell>
                              <TableCell align="right">Carbon Stock (Mg C)</TableCell>
                              <TableCell align="right">Carbon Credits (Mg CO2e)</TableCell>
                              <TableCell>Actions</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {calculationResults.map((result) => (
                              <TableRow key={result.id}>
                                <TableCell>{new Date(result.calculation_date).toLocaleDateString()}</TableCell>
                                <TableCell>
                                  {result.method.charAt(0).toUpperCase() + result.method.slice(1)}
                                </TableCell>
                                <TableCell>{result.baseline_year}</TableCell>
                                <TableCell>{result.project_year}</TableCell>
                                <TableCell align="right">{result.carbon_stock.toLocaleString()}</TableCell>
                                <TableCell align="right">{result.carbon_credits.toLocaleString()}</TableCell>
                                <TableCell>
                                  <Button
                                    size="small"
                                    startIcon={<DownloadIcon />}
                                  >
                                    Export
                                  </Button>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                      
                      <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Button
                          variant="contained"
                          color="primary"
                          onClick={() => setTabValue(0)}
                        >
                          New Calculation
                        </Button>
                      </Box>
                    </>
                  )}
                </Box>
              )}
            </Paper>
          </>
        )}
      </Box>
      
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

export default CarbonCalculation;
