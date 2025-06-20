import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
  Button,
  Alert,
  AlertTitle,
  Skeleton,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  ArrowForward as ArrowForwardIcon,
  ArrowRightAlt as ArrowRightAltIcon,
  Forest as ForestIcon,
  Nature as EcoIcon,
  LocalFireDepartment as CarbonIcon,
  Terrain as TerrainIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  ZoomIn as ZoomInIcon,
  ExpandMore,
  Download,
  Nature,
  ArrowForward,
  Cloud as CloudIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

interface ForestRegion {
  id: string;
  bounding_box: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  area_hectares: number;
  confidence: number;
  forest_type: string;
  density: string;
  health_status: string;
  carbon_density_tC_ha: number;
  biomass_density_t_ha: number;
  carbon_stock_tC: number;
}

interface ColorSpectrumAnalysis {
  detected_imagery_type: string;
  dominant_colors: number[][];
  vegetation_indices: {
    excess_green_index: number;
    vari: number;
    green_leaf_index: number;
  };
  spectral_characteristics: any;
  recommended_analysis_method: string;
}

interface VisualizationData {
  has_visualization: boolean;
  original_image_base64: string;
  annotated_image_base64: string;
  heatmap_overlay_base64: string;
  visualization_type: string;
  bounding_boxes_count: number;
  forest_types_detected: string[];
  description: string;
}

interface ForestDetectionResult {
  total_forest_area_ha: number;
  total_area_analyzed_ha: number;
  forest_coverage_percent: number;
  number_of_forest_regions: number;
  forest_regions: ForestRegion[];
  color_spectrum_analysis: ColorSpectrumAnalysis;
  carbon_metrics: {
    total_carbon_stock_tC: number;
    total_biomass_stock_t: number;
    weighted_carbon_density_tC_ha: number;
    weighted_biomass_density_t_ha: number;
  };
  forest_type_info?: {
    selected_type: string;
    description: string;
    carbon_density_tC_ha: number;
    biomass_density_t_ha: number;
  };
  visualization: VisualizationData;
  confidence_metrics: {
    overall_confidence: number;
    vegetation_confidence: number;
    classification_confidence: number;
  };
  uncertainty_assessment: {
    uncertainty_level: string;
    uncertainty_percentage: number;
    recommended_buffer_percentage: number;
    vcs_category: string;
  };
  validation_data: {
    input_resolution: [number, number];
    pixel_scale_factor: number;
    processing_method: string;
    visualization_available: boolean;
    vcs_compliant: boolean;
  };
}

interface ForestAnalysisVisualizationProps {
  analysisResult: ForestDetectionResult;
  projectName?: string;
  onClose?: () => void;
}

const ForestAnalysisVisualization: React.FC<ForestAnalysisVisualizationProps> = ({
  analysisResult,
  projectName,
  onClose
}) => {
  const [showHeatmap, setShowHeatmap] = React.useState(false);
  const [visualizationType, setVisualizationType] = React.useState('boxes');

  // Add safety checks and default values
  const safeResult = {
    total_forest_area_ha: analysisResult?.total_forest_area_ha || 0,
    total_area_analyzed_ha: analysisResult?.total_area_analyzed_ha || 0,
    forest_coverage_percent: analysisResult?.forest_coverage_percent || 0,
    number_of_forest_regions: analysisResult?.number_of_forest_regions || 0,
    forest_regions: analysisResult?.forest_regions || [],
    color_spectrum_analysis: analysisResult?.color_spectrum_analysis || {
      detected_imagery_type: 'unknown',
      dominant_colors: [],
      vegetation_indices: {
        excess_green_index: 0,
        vari: 0,
        green_leaf_index: 0
      },
      spectral_characteristics: {},
      recommended_analysis_method: 'standard'
    },
    carbon_metrics: analysisResult?.carbon_metrics || {
      weighted_carbon_density_tC_ha: 0,
      weighted_biomass_density_t_ha: 0,
      total_carbon_stock_tC: 0,
      total_biomass_stock_t: 0
    },
    forest_type_info: analysisResult?.forest_type_info,
    visualization: analysisResult?.visualization || {
      has_visualization: false,
      original_image_base64: '',
      annotated_image_base64: '',
      heatmap_overlay_base64: '',
      visualization_type: '',
      bounding_boxes_count: 0,
      forest_types_detected: [],
      description: ''
    },
    confidence_metrics: analysisResult?.confidence_metrics || {
      overall_confidence: 0,
      vegetation_confidence: 0,
      classification_confidence: 0
    },
    uncertainty_assessment: analysisResult?.uncertainty_assessment || {
      uncertainty_level: '',
      uncertainty_percentage: 0,
      recommended_buffer_percentage: 0,
      vcs_category: ''
    },
    validation_data: analysisResult?.validation_data || {
      input_resolution: [0, 0],
      pixel_scale_factor: 0,
      processing_method: '',
      visualization_available: false,
      vcs_compliant: false
    }
  };

  const getImageryTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'rgb_natural': '#4caf50',
      'false_color': '#ff9800',
      'ndvi': '#2196f3',
      'multispectral': '#9c27b0',
      'thermal': '#f44336',
      'sar': '#607d8b',
      'lidar': '#795548'
    };
    return colors[type] || '#9e9e9e';
  };

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'stressed': return 'warning';
      case 'degraded': return 'error';
      default: return 'default';
    }
  };

  const getDensityIcon = (density: string) => {
    switch (density) {
      case 'dense': return '🌲🌲🌲';
      case 'medium': return '🌲🌲';
      case 'sparse': return '🌲';
      default: return '🌲';
    }
  };

  const downloadImage = (base64: string, filename: string) => {
    const link = document.createElement('a');
    link.href = `data:image/jpeg;base64,${base64}`;
    link.download = filename;
    link.click();
  };

  // Check if we have valid visualization data
  if (!safeResult.visualization.original_image_base64) {
    return (
      <Box sx={{ width: '100%', p: 2 }}>
        <Alert severity="error">
          <AlertTitle>Invalid Analysis Result</AlertTitle>
          The analysis result is missing required visualization data. Please try uploading the image again.
        </Alert>
        {onClose && (
          <Button onClick={onClose} variant="outlined" sx={{ mt: 2 }}>
            Close
          </Button>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ForestIcon color="primary" />
          Forest Analysis Results
          {projectName && <Typography variant="body1" color="text.secondary">- {projectName}</Typography>}
        </Typography>
        {onClose && (
          <Button onClick={onClose} variant="outlined">
            Close
          </Button>
        )}
      </Box>

      {/* Color Spectrum Analysis Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <AlertTitle>Automatic Detection Complete</AlertTitle>
        <Typography variant="body2">
          Imagery Type: <strong>{safeResult.color_spectrum_analysis.detected_imagery_type.replace('_', ' ').toUpperCase()}</strong>
          {' • '}
          Analysis Method: <strong>{safeResult.color_spectrum_analysis.recommended_analysis_method.replace('_', ' ')}</strong>
        </Typography>
      </Alert>

      {/* Before/After Visualization */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Nature color="primary" />
          Forest Carbon Analysis Results
        </Typography>
        
        {/* hey let's show the forest type info if available */}
        {safeResult.forest_type_info && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <AlertTitle>Forest Type Analysis</AlertTitle>
            <Typography variant="body2">
              <strong>Selected Type:</strong> {safeResult.forest_type_info.selected_type || 'Mixed'}<br/>
              {safeResult.forest_type_info.description && (
                <>
                  <strong>Description:</strong> {safeResult.forest_type_info.description}<br/>
                </>
              )}
              <strong>Carbon Density:</strong> {safeResult.forest_type_info.carbon_density_tC_ha?.toFixed(1) || '100.0'} tC/ha<br/>
              <strong>Biomass Density:</strong> {safeResult.forest_type_info.biomass_density_t_ha?.toFixed(1) || '200.0'} t/ha
            </Typography>
          </Alert>
        )}
        
        {/* Image Visualization Section */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Forest Detection Visualization
          </Typography>
          
          {/* Toggle for visualization type */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2, gap: 1 }}>
            <Button
              variant={visualizationType === 'boxes' ? 'contained' : 'outlined'}
              onClick={() => setVisualizationType('boxes')}
              size="small"
            >
              Forest Overlay
            </Button>
            <Button
              variant={visualizationType === 'heatmap' ? 'contained' : 'outlined'}
              onClick={() => setVisualizationType('heatmap')}
              size="small"
            >
              Carbon Density Heatmap
            </Button>
          </Box>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={5}>
              <Box>
                <Typography variant="subtitle2" align="center" gutterBottom>
                  Original Image
                </Typography>
                {safeResult.visualization.original_image_base64 ? (
                  <Box
                    component="img"
                    src={`data:image/jpeg;base64,${safeResult.visualization.original_image_base64}`}
                    alt="Original forest image"
                    sx={{ 
                      width: '100%', 
                      height: 'auto',
                      borderRadius: 1,
                      boxShadow: 2
                    }}
                  />
                ) : (
                  <Skeleton variant="rectangular" height={300} />
                )}
              </Box>
            </Grid>
            
            <Grid item xs={12} md={2} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArrowForward sx={{ fontSize: 48, color: 'primary.main' }} />
            </Grid>
            
            <Grid item xs={12} md={5}>
              <Box>
                <Typography variant="subtitle2" align="center" gutterBottom>
                  {visualizationType === 'boxes' ? 'Forest Area Detection' : 'Carbon Density Heatmap'}
                </Typography>
                {safeResult.visualization.heatmap_overlay_base64 ? (
                  <Box
                    component="img"
                    src={`data:image/jpeg;base64,${safeResult.visualization.heatmap_overlay_base64}`}
                    alt={visualizationType === 'boxes' ? 'Forest detection' : 'Carbon heatmap'}
                    sx={{ 
                      width: '100%', 
                      height: 'auto',
                      borderRadius: 1,
                      boxShadow: 2
                    }}
                  />
                ) : (
                  <Skeleton variant="rectangular" height={300} />
                )}
              </Box>
            </Grid>
          </Grid>
        </Box>
        
        {/* Summary Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Forest Area
                </Typography>
                <Typography variant="h4">
                  {safeResult.total_forest_area_ha.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  hectares
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Forest Coverage
                </Typography>
                <Typography variant="h4">
                  {safeResult.forest_coverage_percent.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  of total area
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Carbon Stock
                </Typography>
                <Typography variant="h4">
                  {safeResult.carbon_metrics.total_carbon_stock_tC.toFixed(0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  tonnes CO₂e
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Confidence
                </Typography>
                <Typography variant="h4">
                  {(safeResult.confidence_metrics.overall_confidence * 100).toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  analysis confidence
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* Technical Details */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography>Technical Analysis Details</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Color Spectrum Analysis</Typography>
                <Typography variant="body2" color="text.secondary">
                  Imagery Type: {safeResult.color_spectrum_analysis.detected_imagery_type}<br/>
                  Analysis Method: {safeResult.color_spectrum_analysis.recommended_analysis_method}<br/>
                  Processing: {safeResult.validation_data.processing_method}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Uncertainty Assessment</Typography>
                <Typography variant="body2" color="text.secondary">
                  Level: {safeResult.uncertainty_assessment.uncertainty_level}<br/>
                  VCS Compliant: {safeResult.validation_data.vcs_compliant ? 'Yes' : 'No'}<br/>
                  Buffer Applied: {safeResult.uncertainty_assessment.recommended_buffer_percentage}%
                </Typography>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
        
        {/* Download Options */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => downloadImage(safeResult.visualization.heatmap_overlay_base64, `forest-analysis-heatmap.jpg`)}
            disabled={!safeResult.visualization.heatmap_overlay_base64}
          >
            Download Heatmap
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ForestAnalysisVisualization; 