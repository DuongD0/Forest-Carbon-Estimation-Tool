import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  IconButton,
  Dialog,
  DialogContent,
  DialogActions,
  Button,
  Chip,
  Tooltip,
  useTheme,
  alpha
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
  Close as CloseIcon
} from '@mui/icons-material';

export interface GalleryImage {
  id: string;
  name: string;
  url: string;
  thumbnail?: string;
  size: number;
  uploadDate: string;
  metadata?: {
    satellite?: string;
    captureDate?: string;
    resolution?: number;
    bands?: string[];
    coordinates?: {
      lat: number;
      lng: number;
    };
  };
}

interface ImageGalleryProps {
  images: GalleryImage[];
  title?: string;
  maxImages?: number;
  showMetadata?: boolean;
  onImageClick?: (image: GalleryImage) => void;
  onDownload?: (image: GalleryImage) => void;
}

const ImageGallery: React.FC<ImageGalleryProps> = ({
  images,
  title = "Image Gallery",
  maxImages,
  showMetadata = true,
  onImageClick,
  onDownload
}) => {
  const [selectedImage, setSelectedImage] = useState<GalleryImage | null>(null);
  const theme = useTheme();

  const displayImages = maxImages ? images.slice(0, maxImages) : images;

  const handleImageClick = (image: GalleryImage) => {
    if (onImageClick) {
      onImageClick(image);
    } else {
      setSelectedImage(image);
    }
  };

  const handleCloseDialog = () => {
    setSelectedImage(null);
  };

  const handleDownload = (image: GalleryImage, event: React.MouseEvent) => {
    event.stopPropagation();
    if (onDownload) {
      onDownload(image);
    } else {
      // Default download behavior
      const link = document.createElement('a');
      link.href = image.url;
      link.download = image.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (images.length === 0) {
    return (
      <Box
        sx={{
          p: 4,
          textAlign: 'center',
          backgroundColor: alpha(theme.palette.grey[100], 0.5),
          borderRadius: 2,
          border: `1px dashed ${theme.palette.grey[300]}`
        }}
      >
        <Typography variant="body2" color="text.secondary">
          No images uploaded yet
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title} ({images.length})
        </Typography>
      )}
      
      <Grid container spacing={2}>
        {displayImages.map((image) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={image.id}>
            <Card
              sx={{
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[8]
                }
              }}
              onClick={() => handleImageClick(image)}
            >
              <Box sx={{ position: 'relative' }}>
                <CardMedia
                  component="img"
                  height="140"
                  image={image.thumbnail || image.url}
                  alt={image.name}
                  sx={{ objectFit: 'cover' }}
                />
                <Box
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    display: 'flex',
                    gap: 0.5
                  }}
                >
                  <Tooltip title="View full size">
                    <IconButton
                      size="small"
                      sx={{
                        backgroundColor: alpha(theme.palette.common.white, 0.9),
                        '&:hover': {
                          backgroundColor: theme.palette.common.white
                        }
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedImage(image);
                      }}
                    >
                      <ZoomInIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Download">
                    <IconButton
                      size="small"
                      sx={{
                        backgroundColor: alpha(theme.palette.common.white, 0.9),
                        '&:hover': {
                          backgroundColor: theme.palette.common.white
                        }
                      }}
                      onClick={(e) => handleDownload(image, e)}
                    >
                      <DownloadIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              
              <CardContent sx={{ p: 2 }}>
                <Typography variant="subtitle2" noWrap title={image.name}>
                  {image.name}
                </Typography>
                
                <Typography variant="caption" color="text.secondary" display="block">
                  {formatFileSize(image.size)} • {new Date(image.uploadDate).toLocaleDateString()}
                </Typography>
                
                {showMetadata && image.metadata && (
                  <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {image.metadata.satellite && (
                      <Chip
                        label={image.metadata.satellite}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                    {image.metadata.resolution && (
                      <Chip
                        label={`${image.metadata.resolution}m`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {maxImages && images.length > maxImages && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Showing {maxImages} of {images.length} images
          </Typography>
        </Box>
      )}

      {/* Full Size Image Dialog */}
      <Dialog
        open={!!selectedImage}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          {selectedImage && (
            <>
              <IconButton
                onClick={handleCloseDialog}
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  zIndex: 1,
                  backgroundColor: alpha(theme.palette.common.black, 0.5),
                  color: 'white',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.common.black, 0.7)
                  }
                }}
              >
                <CloseIcon />
              </IconButton>
              
              <img
                src={selectedImage.url}
                alt={selectedImage.name}
                style={{
                  width: '100%',
                  height: 'auto',
                  maxHeight: '80vh',
                  objectFit: 'contain',
                  display: 'block'
                }}
              />
              
              {showMetadata && selectedImage.metadata && (
                <Box sx={{ p: 2, backgroundColor: alpha(theme.palette.common.black, 0.8), color: 'white' }}>
                  <Typography variant="h6" gutterBottom>
                    {selectedImage.name}
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2">
                        <strong>Size:</strong> {formatFileSize(selectedImage.size)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Uploaded:</strong> {new Date(selectedImage.uploadDate).toLocaleString()}
                      </Typography>
                    </Grid>
                    
                    {selectedImage.metadata && (
                      <Grid item xs={12} sm={6}>
                        {selectedImage.metadata.satellite && (
                          <Typography variant="body2">
                            <strong>Satellite:</strong> {selectedImage.metadata.satellite}
                          </Typography>
                        )}
                        {selectedImage.metadata.captureDate && (
                          <Typography variant="body2">
                            <strong>Capture Date:</strong> {new Date(selectedImage.metadata.captureDate).toLocaleDateString()}
                          </Typography>
                        )}
                        {selectedImage.metadata.resolution && (
                          <Typography variant="body2">
                            <strong>Resolution:</strong> {selectedImage.metadata.resolution}m
                          </Typography>
                        )}
                        {selectedImage.metadata.coordinates && (
                          <Typography variant="body2">
                            <strong>Coordinates:</strong> {selectedImage.metadata.coordinates.lat.toFixed(6)}, {selectedImage.metadata.coordinates.lng.toFixed(6)}
                          </Typography>
                        )}
                      </Grid>
                    )}
                  </Grid>
                  
                  {selectedImage.metadata?.bands && selectedImage.metadata.bands.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" gutterBottom>
                        <strong>Spectral Bands:</strong>
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {selectedImage.metadata.bands.map((band, index) => (
                          <Chip
                            key={index}
                            label={band}
                            size="small"
                            sx={{ backgroundColor: alpha(theme.palette.primary.main, 0.2) }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              )}
            </>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
          {selectedImage && (
            <Button
              onClick={(e) => handleDownload(selectedImage, e)}
              startIcon={<DownloadIcon />}
              variant="contained"
            >
              Download
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ImageGallery;