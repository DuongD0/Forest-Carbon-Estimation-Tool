import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Satellite as SatelliteIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import ImageUpload, { UploadedFile } from './ImageUpload';

export interface ImageryMetadata {
  satellite: string;
  captureDate: string;
  resolution: number; // meters per pixel
  bands: string[];
  cloudCover: number; // percentage
  coordinates: {
    lat: number;
    lng: number;
  } | null;
  boundingBox: {
    north: number;
    south: number;
    east: number;
    west: number;
  } | null;
  projection: string;
  notes: string;
}

interface ForestImageryUploadProps {
  onImagesUploaded: (files: File[], metadata: ImageryMetadata[]) => void;
  onUploadProgress?: (progress: number) => void;
  projectId?: string;
  disabled?: boolean;
}

const SATELLITE_OPTIONS = [
  { value: 'landsat-8', label: 'Landsat 8', resolution: 30 },
  { value: 'landsat-9', label: 'Landsat 9', resolution: 30 },
  { value: 'sentinel-2', label: 'Sentinel-2', resolution: 10 },
  { value: 'modis', label: 'MODIS', resolution: 250 },
  { value: 'worldview-2', label: 'WorldView-2', resolution: 0.5 },
  { value: 'worldview-3', label: 'WorldView-3', resolution: 0.3 },
  { value: 'quickbird', label: 'QuickBird', resolution: 0.6 },
  { value: 'ikonos', label: 'IKONOS', resolution: 1 },
  { value: 'spot-6', label: 'SPOT-6', resolution: 1.5 },
  { value: 'spot-7', label: 'SPOT-7', resolution: 1.5 },
  { value: 'planetscope', label: 'PlanetScope', resolution: 3 },
  { value: 'rapideye', label: 'RapidEye', resolution: 5 },
  { value: 'drone', label: 'Drone/UAV', resolution: 0.1 },
  { value: 'aerial', label: 'Aerial Photography', resolution: 0.2 },
  { value: 'other', label: 'Other', resolution: 1 }
];

const BAND_OPTIONS = [
  'Red', 'Green', 'Blue', 'Near-Infrared (NIR)', 'Short-wave Infrared (SWIR1)', 
  'Short-wave Infrared (SWIR2)', 'Thermal Infrared', 'Panchromatic', 
  'Coastal/Aerosol', 'Cirrus', 'RGB Composite', 'False Color Composite',
  'NDVI', 'EVI', 'SAVI', 'NDWI'
];

const PROJECTION_OPTIONS = [
  'WGS84 (EPSG:4326)',
  'Web Mercator (EPSG:3857)',
  'UTM Zone (specify)',
  'State Plane (specify)',
  'Albers Equal Area',
  'Lambert Conformal Conic',
  'Other (specify)'
];

const ForestImageryUpload: React.FC<ForestImageryUploadProps> = ({
  onImagesUploaded,
  onUploadProgress,
  projectId,
  disabled = false
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [metadataList, setMetadataList] = useState<ImageryMetadata[]>([]);
  const [showMetadataDialog, setShowMetadataDialog] = useState(false);
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [bulkMetadata, setBulkMetadata] = useState<Partial<ImageryMetadata>>({
    satellite: '',
    captureDate: '',
    resolution: 30,
    bands: [],
    cloudCover: 0,
    coordinates: null,
    boundingBox: null,
    projection: 'WGS84 (EPSG:4326)',
    notes: ''
  });
  const [applyToAll, setApplyToAll] = useState(true);

  const handleFilesSelected = useCallback((files: File[]) => {
    setUploadedFiles(files);
    
    // Initialize metadata with automatic defaults - no manual selection needed
    const autoMetadata: ImageryMetadata[] = files.map(() => ({
      satellite: 'automatic',  // Will be detected by AI
      captureDate: new Date().toISOString().split('T')[0],  // Today's date as default
      resolution: 1.0,  // Will be refined by the analysis
      bands: ['automatic'],  // AI will detect the actual bands
      cloudCover: 0,
      coordinates: null,
      boundingBox: null,
      projection: 'WGS84 (EPSG:4326)',
      notes: 'Automatically processed - AI will detect imagery type and bands'
    }));
    
    setMetadataList(autoMetadata);
    
    // Skip the metadata dialog and directly upload
    onImagesUploaded(files, autoMetadata);
    setUploadedFiles([]);
    setMetadataList([]);
  }, [onImagesUploaded]);

  const handleMetadataChange = (field: keyof ImageryMetadata, value: any) => {
    setBulkMetadata(prev => ({
      ...prev,
      [field]: value
    }));

    if (applyToAll) {
      setMetadataList(prev => 
        prev.map(metadata => ({
          ...metadata,
          [field]: value
        }))
      );
    } else {
      setMetadataList(prev => 
        prev.map((metadata, index) => 
          index === currentFileIndex 
            ? { ...metadata, [field]: value }
            : metadata
        )
      );
    }
  };

  const handleSatelliteChange = (satellite: string) => {
    const selectedSatellite = SATELLITE_OPTIONS.find(s => s.value === satellite);
    if (selectedSatellite) {
      handleMetadataChange('satellite', satellite);
      handleMetadataChange('resolution', selectedSatellite.resolution);
    }
  };

  const handleBandToggle = (band: string) => {
    const currentBands = applyToAll 
      ? bulkMetadata.bands || []
      : metadataList[currentFileIndex]?.bands || [];
    
    const newBands = currentBands.includes(band)
      ? currentBands.filter(b => b !== band)
      : [...currentBands, band];
    
    handleMetadataChange('bands', newBands);
  };

  const handleCoordinatesChange = (field: 'lat' | 'lng', value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      const currentCoords = applyToAll 
        ? bulkMetadata.coordinates 
        : metadataList[currentFileIndex]?.coordinates;
      
      const newCoords = {
        lat: field === 'lat' ? numValue : currentCoords?.lat || 0,
        lng: field === 'lng' ? numValue : currentCoords?.lng || 0
      };
      
      handleMetadataChange('coordinates', newCoords);
    }
  };

  const handleBoundingBoxChange = (field: 'north' | 'south' | 'east' | 'west', value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      const currentBBox = applyToAll 
        ? bulkMetadata.boundingBox 
        : metadataList[currentFileIndex]?.boundingBox;
      
      const newBBox = {
        north: field === 'north' ? numValue : currentBBox?.north || 0,
        south: field === 'south' ? numValue : currentBBox?.south || 0,
        east: field === 'east' ? numValue : currentBBox?.east || 0,
        west: field === 'west' ? numValue : currentBBox?.west || 0
      };
      
      handleMetadataChange('boundingBox', newBBox);
    }
  };

  const handleNextFile = () => {
    if (currentFileIndex < uploadedFiles.length - 1) {
      setCurrentFileIndex(currentFileIndex + 1);
    }
  };

  const handlePreviousFile = () => {
    if (currentFileIndex > 0) {
      setCurrentFileIndex(currentFileIndex - 1);
    }
  };

  const handleSubmitMetadata = () => {
    // Validate required fields
    const hasValidMetadata = metadataList.every(metadata => 
      metadata.satellite && metadata.captureDate
    );

    if (!hasValidMetadata) {
      alert('Please fill in at least the satellite and capture date for all images.');
      return;
    }

    onImagesUploaded(uploadedFiles, metadataList);
    setShowMetadataDialog(false);
    setUploadedFiles([]);
    setMetadataList([]);
  };

  const getCurrentMetadata = () => {
    return applyToAll ? bulkMetadata : metadataList[currentFileIndex];
  };

  const currentMetadata = getCurrentMetadata();

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Forest Imagery Upload
      </Typography>
      
      <Alert severity="success" sx={{ mb: 2 }}>
        <Typography variant="body2">
          Upload satellite imagery, aerial photos, or drone images of forest areas. 
          <strong> Our AI will automatically detect forest types and calculate carbon content.</strong>
          <br />
          <strong>✓ No manual configuration needed</strong> - The system will automatically:
          <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
            <li>Detect imagery type and spectral bands</li>
            <li>Identify forest regions and types</li>
            <li>Calculate carbon content</li>
          </ul>
          Supported formats: GeoTIFF, JPEG, PNG, and other common image formats.
        </Typography>
      </Alert>

      <ImageUpload
        onFilesSelected={handleFilesSelected}
        maxFiles={20}
        maxFileSize={100} // 100MB for satellite imagery
        acceptedFormats={[
          'image/tiff', 'image/tif', 'image/geotiff',
          'image/jpeg', 'image/jpg', 'image/png', 
          'image/gif', 'image/webp', 'image/bmp'
        ]}
        title="Upload Forest Imagery"
        description="Drag and drop satellite images, aerial photos, or drone imagery here. The system will automatically detect forest types."
        disabled={disabled}
        showPreview={true}
        multiple={true}
      />

      {/* Metadata Collection Dialog */}
      <Dialog
        open={showMetadataDialog}
        onClose={() => setShowMetadataDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <SatelliteIcon />
            <Typography variant="h6">
              Image Metadata
            </Typography>
            {uploadedFiles.length > 1 && (
              <Chip 
                label={`${currentFileIndex + 1} of ${uploadedFiles.length}`}
                size="small"
                color="primary"
              />
            )}
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {uploadedFiles.length > 1 && (
            <FormControlLabel
              control={
                <Checkbox
                  checked={applyToAll}
                  onChange={(e) => setApplyToAll(e.target.checked)}
                />
              }
              label="Apply metadata to all images"
              sx={{ mb: 2 }}
            />
          )}

          {!applyToAll && uploadedFiles.length > 1 && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Currently editing metadata for: <strong>{uploadedFiles[currentFileIndex]?.name}</strong>
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                <SatelliteIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Satellite/Source</InputLabel>
                <Select
                  value={currentMetadata?.satellite || ''}
                  onChange={(e) => handleSatelliteChange(e.target.value)}
                  label="Satellite/Source"
                >
                  {SATELLITE_OPTIONS.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label} ({option.resolution}m resolution)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                type="date"
                label="Capture Date"
                value={currentMetadata?.captureDate || ''}
                onChange={(e) => handleMetadataChange('captureDate', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Resolution (meters per pixel)"
                value={currentMetadata?.resolution || ''}
                onChange={(e) => handleMetadataChange('resolution', parseFloat(e.target.value))}
                inputProps={{ min: 0, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Cloud Cover (%)"
                value={currentMetadata?.cloudCover || ''}
                onChange={(e) => handleMetadataChange('cloudCover', parseFloat(e.target.value))}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>

            {/* Spectral Bands */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">
                    Spectral Bands
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Select the spectral bands available in this imagery:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {BAND_OPTIONS.map(band => (
                        <Chip
                          key={band}
                          label={band}
                          clickable
                          color={currentMetadata?.bands?.includes(band) ? 'primary' : 'default'}
                          onClick={() => handleBandToggle(band)}
                        />
                      ))}
                    </Box>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Geographic Information */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">
                    <LocationIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Geographic Information
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Coordinate System</InputLabel>
                        <Select
                          value={currentMetadata?.projection || ''}
                          onChange={(e) => handleMetadataChange('projection', e.target.value)}
                          label="Coordinate System"
                        >
                          {PROJECTION_OPTIONS.map(proj => (
                            <MenuItem key={proj} value={proj}>
                              {proj}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Center Coordinates
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Latitude"
                        value={currentMetadata?.coordinates?.lat || ''}
                        onChange={(e) => handleCoordinatesChange('lat', e.target.value)}
                        inputProps={{ step: 0.000001 }}
                      />
                    </Grid>
                    
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Longitude"
                        value={currentMetadata?.coordinates?.lng || ''}
                        onChange={(e) => handleCoordinatesChange('lng', e.target.value)}
                        inputProps={{ step: 0.000001 }}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Bounding Box (Optional)
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="North"
                        value={currentMetadata?.boundingBox?.north || ''}
                        onChange={(e) => handleBoundingBoxChange('north', e.target.value)}
                        inputProps={{ step: 0.000001 }}
                      />
                    </Grid>
                    
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="South"
                        value={currentMetadata?.boundingBox?.south || ''}
                        onChange={(e) => handleBoundingBoxChange('south', e.target.value)}
                        inputProps={{ step: 0.000001 }}
                      />
                    </Grid>
                    
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="East"
                        value={currentMetadata?.boundingBox?.east || ''}
                        onChange={(e) => handleBoundingBoxChange('east', e.target.value)}
                        inputProps={{ step: 0.000001 }}
                      />
                    </Grid>
                    
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="West"
                        value={currentMetadata?.boundingBox?.west || ''}
                        onChange={(e) => handleBoundingBoxChange('west', e.target.value)}
                        inputProps={{ step: 0.000001 }}
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Additional Notes */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Additional Notes"
                value={currentMetadata?.notes || ''}
                onChange={(e) => handleMetadataChange('notes', e.target.value)}
                placeholder="Any additional information about this imagery..."
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions>
          {!applyToAll && uploadedFiles.length > 1 && (
            <Box sx={{ flexGrow: 1 }}>
              <Button 
                onClick={handlePreviousFile}
                disabled={currentFileIndex === 0}
              >
                Previous
              </Button>
              <Button 
                onClick={handleNextFile}
                disabled={currentFileIndex === uploadedFiles.length - 1}
              >
                Next
              </Button>
            </Box>
          )}
          
          <Button onClick={() => setShowMetadataDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitMetadata}
            variant="contained"
            color="primary"
          >
            Upload Images
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ForestImageryUpload;