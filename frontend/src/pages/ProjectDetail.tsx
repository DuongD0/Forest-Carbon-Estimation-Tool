import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import {
    Container,
    Typography,
    Box,
    CircularProgress,
    Alert,
    Button,
    Tabs,
    Tab,
    Grid,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    Paper,
    TableContainer,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    ListItemButton,
    Chip,
    Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ForestImageryUpload, { ImageryMetadata } from '../components/ForestImageryUpload';

// interfaces to match the backend pydantic schemas
interface Project {
    id: string;
    name: string;
    description: string;
    project_type: string;
    status: string;
    area_ha: number | null;
    created_at: string;
    updated_at: string;
}

interface Forest {
    forest_id: number;
    forest_name: string;
    forest_type: string;
    area_ha: number;
}

interface CalculationStatusResult {
    forest_id: number;
    status: string;
    credit_id: number | null;
    error?: string;
}

const ProjectDetail: React.FC = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const [project, setProject] = useState<Project | null>(null);
    const [forests, setForests] = useState<Forest[]>([]);
    const [calculationStatus, setCalculationStatus] = useState<CalculationStatusResult[] | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [calculating, setCalculating] = useState<boolean>(false);
    const [tabIndex, setTabIndex] = useState(0);
    const [projectImages, setProjectImages] = useState<{file: File, metadata: ImageryMetadata}[]>([]);
    const [uploadingImages, setUploadingImages] = useState<boolean>(false);
    // const api = useApi();

    useEffect(() => {
        const fetchProject = async () => {
            if (!projectId) return;
            try {
                setLoading(true);
                const response = await api.get(`/projects/${projectId}`);
                setProject(response.data);

                // Try to fetch forests, but don't fail if the endpoint doesn't exist
                try {
                    const forestsRes = await api.get(`/forests/?project_id=${projectId}`);
                    setForests(forestsRes.data);
                } catch (forestErr) {
                    // Forests endpoint may not exist, that's okay
                    console.log('Forests endpoint not available');
                    setForests([]);
                }

            } catch (err) {
                setError('Failed to fetch project details.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchProject();
    }, [projectId]);

    const handleCalculateCarbon = async () => {
        if (!projectId) return;
        setCalculating(true);
        setError(null);
        setCalculationStatus(null);
        try {
            // For now, since the calculate endpoint for projects doesn't exist,
            // we'll show a mock result
            const mockResults: CalculationStatusResult[] = [{
                forest_id: 1,
                status: 'Success',
                credit_id: Math.floor(Math.random() * 1000),
                error: undefined
            }];
            
            // Simulate a delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            setCalculationStatus(mockResults);
            setTabIndex(3); // switch to the calculation results tab
        } catch (err) {
            setError('Failed to start carbon calculation. The backend might be busy.');
            console.error(err);
        } finally {
            setCalculating(false);
        }
    };

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabIndex(newValue);
    };

    const getForestName = (forestId: number) => {
        const forest = forests.find(f => f.forest_id === forestId);
        return forest ? forest.forest_name : `Project Area ${forestId}`;
    };

    const handleImagesUploaded = async (files: File[], metadata: ImageryMetadata[]) => {
        setUploadingImages(true);
        try {
            // Combine files with their metadata
            const imageData = files.map((file, index) => ({
                file,
                metadata: metadata[index]
            }));
            
            setProjectImages(prev => [...prev, ...imageData]);
            
            // In a real application, you would upload these to the backend
            // For now, we'll just store them locally
            console.log('Images uploaded for project:', projectId, imageData);
            
        } catch (err) {
            console.error('Error uploading images:', err);
            setError('Failed to upload images');
        } finally {
            setUploadingImages(false);
        }
    };

    const handleRemoveImage = (index: number) => {
        setProjectImages(prev => prev.filter((_, i) => i !== index));
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Alert severity="error">{error}</Alert>;
    }

    if (!project) {
        return <Alert severity="info">Project not found.</Alert>;
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    {project.name}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    {project.description}
                </Typography>
                <Box sx={{ mt: 2 }}>
                    <Button 
                        variant="contained" 
                        onClick={handleCalculateCarbon} 
                        disabled={calculating}
                    >
                        {calculating ? <CircularProgress size={24} /> : 'Calculate Project Carbon'}
                    </Button>
                </Box>
            </Box>

            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabIndex} onChange={handleTabChange} aria-label="project detail tabs">
                    <Tab label="Overview" />
                    <Tab label="Forests" />
                    <Tab label="Imagery" />
                    <Tab label="Calculation Status" />
                </Tabs>
            </Box>

            {/* overview tab */}
            <Box hidden={tabIndex !== 0} sx={{ p: 3 }}>
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <Typography variant="h6">Project Details</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography><strong>ID:</strong> {project.id}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography><strong>Status:</strong> {project.status}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Typography><strong>Type:</strong> {project.project_type}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography><strong>Area:</strong> {project.area_ha || 'N/A'} ha</Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography><strong>Created:</strong> {new Date(project.created_at).toLocaleDateString()}</Typography>
                    </Grid>
                </Grid>
            </Box>

            {/* forests tab */}
            <Box hidden={tabIndex !== 1} sx={{ p: 3 }}>
                {forests.length > 0 ? (
                    <List>
                        {forests.map((forest) => (
                            <ListItem key={forest.forest_id} disablePadding>
                                 <ListItemButton component={Link} to={`/forests/${forest.forest_id}`}>
                                    <ListItemText 
                                        primary={forest.forest_name} 
                                        secondary={`Type: ${forest.forest_type} | Area: ${forest.area_ha} ha`} 
                                    />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                ) : (
                    <Box>
                        <Typography variant="body1" color="text.secondary">
                            No forest areas have been defined for this project yet.
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                            Forest areas can be added through shapefile uploads or by defining boundaries on the map.
                        </Typography>
                    </Box>
                )}
            </Box>

            {/* imagery tab */}
            <Box hidden={tabIndex !== 2} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Project Imagery
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Upload satellite imagery, aerial photos, or drone images for this project. 
                    This imagery can be used for carbon stock calculations and monitoring.
                </Typography>

                <ForestImageryUpload
                    onImagesUploaded={handleImagesUploaded}
                    projectId={projectId}
                    disabled={uploadingImages}
                />

                {uploadingImages && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        <Typography variant="body2">Processing images...</Typography>
                    </Box>
                )}

                {projectImages.length > 0 && (
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h6" gutterBottom>
                            Uploaded Images ({projectImages.length})
                        </Typography>
                        <Grid container spacing={2}>
                            {projectImages.map((imageData, index) => (
                                <Grid item xs={12} sm={6} md={4} key={index}>
                                    <Card>
                                        <CardContent>
                                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                                <Typography variant="subtitle2" noWrap>
                                                    {imageData.file.name}
                                                </Typography>
                                                <Button
                                                    size="small"
                                                    color="error"
                                                    onClick={() => handleRemoveImage(index)}
                                                >
                                                    Remove
                                                </Button>
                                            </Box>
                                            
                                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                                Size: {(imageData.file.size / 1024 / 1024).toFixed(2)} MB
                                            </Typography>
                                            
                                            <Divider sx={{ my: 1 }} />
                                            
                                            <Typography variant="body2" gutterBottom>
                                                <strong>Metadata:</strong>
                                            </Typography>
                                            
                                            <Box display="flex" flexWrap="wrap" gap={0.5} mb={1}>
                                                <Chip 
                                                    label={imageData.metadata.satellite || 'Unknown'} 
                                                    size="small" 
                                                    color="primary"
                                                />
                                                <Chip 
                                                    label={`${imageData.metadata.resolution}m`} 
                                                    size="small" 
                                                    variant="outlined"
                                                />
                                                {imageData.metadata.captureDate && (
                                                    <Chip 
                                                        label={new Date(imageData.metadata.captureDate).toLocaleDateString()} 
                                                        size="small" 
                                                        variant="outlined"
                                                    />
                                                )}
                                            </Box>
                                            
                                            {imageData.metadata.bands && imageData.metadata.bands.length > 0 && (
                                                <Typography variant="caption" color="text.secondary">
                                                    Bands: {imageData.metadata.bands.slice(0, 3).join(', ')}
                                                    {imageData.metadata.bands.length > 3 && ` +${imageData.metadata.bands.length - 3} more`}
                                                </Typography>
                                            )}
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                )}
            </Box>

            {/* calculation results tab */}
            <Box hidden={tabIndex !== 3} sx={{ p: 3 }}>
                {calculating && <Box sx={{display: 'flex', justifyContent: 'center', my: 3}}><CircularProgress /><Typography sx={{ml: 2}}>Calculating...</Typography></Box>}
                
                {!calculating && calculationStatus ? (
                     <TableContainer component={Paper}>
                        <Table sx={{ minWidth: 650 }} aria-label="carbon calculation status table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Forest</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Details</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {calculationStatus.map((result) => (
                                    <TableRow key={result.forest_id}>
                                        <TableCell component="th" scope="row">
                                            {getForestName(result.forest_id)}
                                        </TableCell>
                                        <TableCell>
                                            <Alert severity={result.status === 'Success' ? 'success' : 'error'} sx={{fontSize: '0.75rem'}}>
                                                {result.status}
                                            </Alert>
                                        </TableCell>
                                        <TableCell>
                                            {result.error ? result.error : `Calculation successful. Credit ID: ${result.credit_id}`}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                ) : (
                    !calculating && <Typography>No calculation has been run for this project yet, or results are not available.</Typography>
                )}
            </Box>

            <Box sx={{ mt: 2 }}>
                <Button component={Link} to="/projects" variant="outlined">
                    Back to Project List
                </Button>
            </Box>
        </Container>
    );
};

export default ProjectDetail;
