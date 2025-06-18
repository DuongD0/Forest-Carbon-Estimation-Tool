import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardMedia,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Close as CloseIcon,
  Image as ImageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

export interface UploadedFile {
  file: File;
  id: string;
  preview: string;
  status: 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

interface ImageUploadProps {
  onFilesSelected: (files: File[]) => void;
  onFileRemove?: (fileId: string) => void;
  onUploadProgress?: (fileId: string, progress: number) => void;
  onUploadComplete?: (fileId: string, response?: any) => void;
  onUploadError?: (fileId: string, error: string) => void;
  maxFiles?: number;
  maxFileSize?: number; // in MB
  acceptedFormats?: string[];
  multiple?: boolean;
  disabled?: boolean;
  title?: string;
  description?: string;
  showPreview?: boolean;
  autoUpload?: boolean;
  uploadFunction?: (file: File) => Promise<any>;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onFilesSelected,
  onFileRemove,
  onUploadProgress,
  onUploadComplete,
  onUploadError,
  maxFiles = 10,
  maxFileSize = 10, // 10MB default
  acceptedFormats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/tiff'],
  multiple = true,
  disabled = false,
  title = 'Upload Images',
  description = 'Drag and drop images here or click to browse',
  showPreview = true,
  autoUpload = false,
  uploadFunction
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();

  const generateFileId = () => Math.random().toString(36).substr(2, 9);

  const validateFile = (file: File): string | null => {
    if (!acceptedFormats.includes(file.type)) {
      return `File type ${file.type} is not supported. Accepted formats: ${acceptedFormats.join(', ')}`;
    }
    
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File size exceeds ${maxFileSize}MB limit`;
    }
    
    return null;
  };

  const createFilePreview = (file: File): string => {
    return URL.createObjectURL(file);
  };

  const processFiles = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    
    if (uploadedFiles.length + fileArray.length > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const validFiles: File[] = [];
    const newUploadedFiles: UploadedFile[] = [];

    fileArray.forEach(file => {
      const error = validateFile(file);
      const fileId = generateFileId();
      
      if (error) {
        newUploadedFiles.push({
          file,
          id: fileId,
          preview: createFilePreview(file),
          status: 'error',
          progress: 0,
          error
        });
      } else {
        validFiles.push(file);
        newUploadedFiles.push({
          file,
          id: fileId,
          preview: createFilePreview(file),
          status: autoUpload ? 'uploading' : 'success',
          progress: autoUpload ? 0 : 100
        });
      }
    });

    setUploadedFiles(prev => [...prev, ...newUploadedFiles]);
    
    if (validFiles.length > 0) {
      onFilesSelected(validFiles);
      
      if (autoUpload && uploadFunction) {
        // Upload files automatically
        for (const uploadedFile of newUploadedFiles.filter(f => f.status === 'uploading')) {
          try {
            await uploadFile(uploadedFile);
          } catch (error) {
            console.error('Upload failed:', error);
          }
        }
      }
    }
  }, [uploadedFiles, maxFiles, onFilesSelected, autoUpload, uploadFunction]);

  const uploadFile = async (uploadedFile: UploadedFile) => {
    if (!uploadFunction) return;

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === uploadedFile.id 
              ? { ...f, progress: Math.min(f.progress + 10, 90) }
              : f
          )
        );
        onUploadProgress?.(uploadedFile.id, uploadedFile.progress);
      }, 200);

      const response = await uploadFunction(uploadedFile.file);
      
      clearInterval(progressInterval);
      
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === uploadedFile.id 
            ? { ...f, status: 'success', progress: 100 }
            : f
        )
      );
      
      onUploadComplete?.(uploadedFile.id, response);
    } catch (error: any) {
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === uploadedFile.id 
            ? { ...f, status: 'error', error: error.message || 'Upload failed' }
            : f
        )
      );
      
      onUploadError?.(uploadedFile.id, error.message || 'Upload failed');
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFiles(files);
    }
  }, [disabled, processFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  }, [processFiles]);

  const handleRemoveFile = (fileId: string) => {
    const fileToRemove = uploadedFiles.find(f => f.id === fileId);
    if (fileToRemove) {
      URL.revokeObjectURL(fileToRemove.preview);
    }
    
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    onFileRemove?.(fileId);
  };

  const handlePreviewFile = (file: UploadedFile) => {
    setPreviewFile(file);
  };

  const handleClosePreview = () => {
    setPreviewFile(null);
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'uploading':
        return <CloudUploadIcon color="primary" />;
      default:
        return <ImageIcon />;
    }
  };

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      
      {/* Upload Area */}
      <Paper
        sx={{
          p: 3,
          border: `2px dashed ${isDragOver ? theme.palette.primary.main : theme.palette.divider}`,
          backgroundColor: isDragOver 
            ? alpha(theme.palette.primary.main, 0.1)
            : disabled 
              ? theme.palette.action.disabledBackground
              : 'transparent',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: disabled ? theme.palette.divider : theme.palette.primary.main,
            backgroundColor: disabled 
              ? theme.palette.action.disabledBackground 
              : alpha(theme.palette.primary.main, 0.05)
          }
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight={120}
        >
          <CloudUploadIcon 
            sx={{ 
              fontSize: 48, 
              color: disabled ? 'action.disabled' : 'primary.main',
              mb: 2 
            }} 
          />
          <Typography 
            variant="h6" 
            color={disabled ? 'text.disabled' : 'text.primary'}
            gutterBottom
          >
            {description}
          </Typography>
          <Typography 
            variant="body2" 
            color={disabled ? 'text.disabled' : 'text.secondary'}
            textAlign="center"
          >
            Supported formats: {acceptedFormats.map(format => format.split('/')[1]).join(', ')}
            <br />
            Maximum file size: {maxFileSize}MB
            {multiple && ` • Maximum ${maxFiles} files`}
          </Typography>
          <Button
            variant="outlined"
            startIcon={<CloudUploadIcon />}
            sx={{ mt: 2 }}
            disabled={disabled}
          >
            Browse Files
          </Button>
        </Box>
      </Paper>

      <input
        ref={fileInputRef}
        type="file"
        multiple={multiple}
        accept={acceptedFormats.join(',')}
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        disabled={disabled}
      />

      {/* File List */}
      {uploadedFiles.length > 0 && showPreview && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Uploaded Files ({uploadedFiles.length})
          </Typography>
          <Grid container spacing={2}>
            {uploadedFiles.map((uploadedFile) => (
              <Grid item xs={12} sm={6} md={4} key={uploadedFile.id}>
                <Card>
                  <CardMedia
                    component="img"
                    height="140"
                    image={uploadedFile.preview}
                    alt={uploadedFile.file.name}
                    sx={{ objectFit: 'cover' }}
                  />
                  <CardActions sx={{ p: 1, flexDirection: 'column', alignItems: 'stretch' }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                      <Chip
                        icon={getStatusIcon(uploadedFile.status)}
                        label={uploadedFile.status}
                        size="small"
                        color={getStatusColor(uploadedFile.status) as any}
                      />
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handlePreviewFile(uploadedFile)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveFile(uploadedFile.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>
                    
                    <Typography variant="caption" noWrap title={uploadedFile.file.name}>
                      {uploadedFile.file.name}
                    </Typography>
                    
                    <Typography variant="caption" color="text.secondary">
                      {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                    
                    {uploadedFile.status === 'uploading' && (
                      <LinearProgress 
                        variant="determinate" 
                        value={uploadedFile.progress} 
                        sx={{ mt: 1 }}
                      />
                    )}
                    
                    {uploadedFile.error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {uploadedFile.error}
                      </Alert>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={!!previewFile}
        onClose={handleClosePreview}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {previewFile?.file.name}
            </Typography>
            <IconButton onClick={handleClosePreview}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {previewFile && (
            <Box textAlign="center">
              <img
                src={previewFile.preview}
                alt={previewFile.file.name}
                style={{
                  maxWidth: '100%',
                  maxHeight: '70vh',
                  objectFit: 'contain'
                }}
              />
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary">
                  Size: {(previewFile.file.size / 1024 / 1024).toFixed(2)} MB
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Type: {previewFile.file.type}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last Modified: {new Date(previewFile.file.lastModified).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreview}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ImageUpload;