import React from 'react';
import { Box, Typography, Grid, Card, CardContent, CardHeader, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CalculateIcon from '@mui/icons-material/Calculate';
import RecentProjects from '../components/dashboard/RecentProjects';
import RecentForests from '../components/dashboard/RecentForests';
import ImageGallery, { GalleryImage } from '../components/ImageGallery';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();

    // Mock data for recent images - in a real app, this would come from an API
    const recentImages: GalleryImage[] = [
        {
            id: '1',
            name: 'forest_landsat8_2024_01.tif',
            url: 'https://via.placeholder.com/400x300/4CAF50/FFFFFF?text=Forest+Imagery',
            thumbnail: 'https://via.placeholder.com/200x150/4CAF50/FFFFFF?text=Forest+Imagery',
            size: 15728640, // 15MB
            uploadDate: '2024-01-15T10:30:00Z',
            metadata: {
                satellite: 'Landsat 8',
                captureDate: '2024-01-10',
                resolution: 30,
                bands: ['Red', 'Green', 'Blue', 'NIR'],
                coordinates: { lat: 45.5231, lng: -122.6765 }
            }
        },
        {
            id: '2',
            name: 'sentinel2_forest_monitoring.tif',
            url: 'https://via.placeholder.com/400x300/2196F3/FFFFFF?text=Sentinel+2',
            thumbnail: 'https://via.placeholder.com/200x150/2196F3/FFFFFF?text=Sentinel+2',
            size: 23456789, // 23MB
            uploadDate: '2024-01-14T14:20:00Z',
            metadata: {
                satellite: 'Sentinel-2',
                captureDate: '2024-01-12',
                resolution: 10,
                bands: ['Red', 'Green', 'Blue', 'NIR', 'SWIR1'],
                coordinates: { lat: 45.5245, lng: -122.6789 }
            }
        },
        {
            id: '3',
            name: 'drone_survey_area_a.jpg',
            url: 'https://via.placeholder.com/400x300/FF9800/FFFFFF?text=Drone+Survey',
            thumbnail: 'https://via.placeholder.com/200x150/FF9800/FFFFFF?text=Drone+Survey',
            size: 5242880, // 5MB
            uploadDate: '2024-01-13T09:15:00Z',
            metadata: {
                satellite: 'Drone/UAV',
                captureDate: '2024-01-13',
                resolution: 0.1,
                bands: ['RGB Composite'],
                coordinates: { lat: 45.5198, lng: -122.6743 }
            }
        }
    ];

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Dashboard
            </Typography>
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <RecentProjects />
                </Grid>
                <Grid item xs={12} md={6}>
                    <RecentForests />
                </Grid>
                
                <Grid item xs={12}>
                    <Card>
                        <CardHeader title="Recent Forest Imagery" />
                        <CardContent>
                            <ImageGallery 
                                images={recentImages}
                                maxImages={6}
                                showMetadata={true}
                                title=""
                            />
                            {recentImages.length === 0 && (
                                <Box sx={{ textAlign: 'center', py: 4 }}>
                                    <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                                    <Typography variant="body1" color="text.secondary" gutterBottom>
                                        No imagery uploaded yet
                                    </Typography>
                                    <Button
                                        variant="outlined"
                                        startIcon={<CloudUploadIcon />}
                                        onClick={() => navigate('/calculate-carbon')}
                                    >
                                        Upload Forest Imagery
                                    </Button>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardHeader title="Carbon Credits Summary" />
                        <CardContent>
                            <Typography variant="h6" color="primary">
                                Coming Soon
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Carbon credit tracking and analytics will be available here.
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardHeader title="Quick Actions" />
                        <CardContent>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <Button
                                    variant="outlined"
                                    startIcon={<CloudUploadIcon />}
                                    onClick={() => navigate('/calculate-carbon')}
                                    fullWidth
                                >
                                    Upload Forest Imagery
                                </Button>
                                <Button
                                    variant="outlined"
                                    startIcon={<CalculateIcon />}
                                    onClick={() => navigate('/calculate-carbon')}
                                    fullWidth
                                >
                                    Calculate Carbon Credits
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => navigate('/projects')}
                                    fullWidth
                                >
                                    View All Projects
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => navigate('/marketplace')}
                                    fullWidth
                                >
                                    Browse Marketplace
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;
