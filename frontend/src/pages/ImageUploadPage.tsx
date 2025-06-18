import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Alert,
  Button,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImageIcon from '@mui/icons-material/Image';
import ForestImageryUpload, { ImageryMetadata } from '../components/ForestImageryUpload';
import ImageUpload from '../components/ImageUpload';
import ImageGallery, { GalleryImage } from '../components/ImageGallery';

const ImageUploadPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [uploadedImages, setUploadedImages] = useState<GalleryImage[]>([]);
  const [forestImages, setForestImages] = useState<{file: File, metadata: ImageryMetadata}[]>([]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleForestImagesUploaded = (files: File[], metadata: ImageryMetadata[]) => {
    const newImages = files.map((file, index) => ({
      file,
      metadata: metadata[index]
    }));
    
    setForestImages(prev => [...prev, ...newImages]);
    
    // Convert to gallery format for display
    const galleryImages: GalleryImage[] = newImages.map((item, index) => ({
      id: `forest-${Date.now()}-${index}`,
      name: item.file.name,
      url: URL.createObjectURL(item.file),
      size: item.file.size,
      uploadDate: new Date().toISOString(),
      metadata: {
        satellite: item.metadata.satellite,
        captureDate: item.metadata.captureDate,
        resolution: item.metadata.resolution,
        bands: item.metadata.bands,
        coordinates: item.metadata.coordinates || undefined
      }
    }));
    
    setUploadedImages(prev => [...prev, ...galleryImages]);
  };

  const handleGeneralImagesUploaded = (files: File[]) => {
    const galleryImages: GalleryImage[] = files.map((file, index) => ({
      id: `general-${Date.now()}-${index}`,
      name: file.name,
      url: URL.createObjectURL(file),
      size: file.size,
      uploadDate: new Date().toISOString()
    }));
    
    setUploadedImages(prev => [...prev, ...galleryImages]);
  };

  const handleImageRemove = (imageId: string) => {
    setUploadedImages(prev => {
      const imageToRemove = prev.find(img => img.id === imageId);
      if (imageToRemove) {
        URL.revokeObjectURL(imageToRemove.url);
      }
      return prev.filter(img => img.id !== imageId);
    });
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Image Upload & Management
        </Typography>
        <Typography paragraph color="text.secondary">
          Upload and manage forest imagery, satellite data, and other project-related images.
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab 
              label="Forest Imagery" 
              icon={<CloudUploadIcon />} 
              iconPosition="start"
            />
            <Tab 
              label="General Images" 
              icon={<ImageIcon />} 
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {/* Forest Imagery Tab */}
        <Box hidden={tabValue !== 0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 3 }}>
                Upload satellite imagery, aerial photos, or drone images with detailed metadata 
                for accurate carbon stock calculations and forest monitoring.
              </Alert>
              
              <ForestImageryUpload
                onImagesUploaded={handleForestImagesUploaded}
                disabled={false}
              />
            </Grid>
          </Grid>
        </Box>

        {/* General Images Tab */}
        <Box hidden={tabValue !== 1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 3 }}>
                Upload general project images, documentation photos, or reference materials.
              </Alert>
              
              <ImageUpload
                onFilesSelected={handleGeneralImagesUploaded}
                maxFiles={50}
                maxFileSize={25}
                title="Upload General Images"
                description="Drag and drop images here or click to browse"
                showPreview={true}
                multiple={true}
              />
            </Grid>
          </Grid>
        </Box>

        {/* Uploaded Images Gallery */}
        {uploadedImages.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 3 }} />
            <Typography variant="h5" gutterBottom>
              Uploaded Images
            </Typography>
            
            <ImageGallery
              images={uploadedImages}
              title=""
              showMetadata={true}
              onImageClick={(image) => {
                console.log('Image clicked:', image);
              }}
              onDownload={(image) => {
                console.log('Download image:', image);
              }}
            />
            
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button
                variant="outlined"
                color="error"
                onClick={() => {
                  uploadedImages.forEach(img => URL.revokeObjectURL(img.url));
                  setUploadedImages([]);
                  setForestImages([]);
                }}
              >
                Clear All Images
              </Button>
            </Box>
          </Box>
        )}

        {/* Statistics */}
        {uploadedImages.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 3 }} />
            <Typography variant="h6" gutterBottom>
              Upload Statistics
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {uploadedImages.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Images
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {forestImages.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Forest Imagery
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {(uploadedImages.reduce((total, img) => total + img.size, 0) / 1024 / 1024).toFixed(1)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Size (MB)
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {new Set(uploadedImages.map(img => img.metadata?.satellite).filter(Boolean)).size}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Satellite Sources
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default ImageUploadPage;