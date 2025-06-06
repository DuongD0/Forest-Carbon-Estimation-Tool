import React, { useState, useEffect } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import api from '../services/api';
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
    ListItemButton
} from '@mui/material';

// Interfaces matching the backend Pydantic schemas
interface Project {
    project_id: number;
    project_name: string;
    description: string;
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

    useEffect(() => {
        const fetchProjectDetails = async () => {
            if (!projectId) return;
            try {
                setLoading(true);
                const projectRes = await api.get(`/projects/${projectId}`);
                setProject(projectRes.data);

                const forestsRes = await api.get(`/forests/?project_id=${projectId}`);
                setForests(forestsRes.data);

            } catch (err) {
                setError('Failed to fetch project details.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchProjectDetails();
    }, [projectId]);

    const handleCalculateCarbon = async () => {
        if (!projectId) return;
        setCalculating(true);
        setError(null);
        setCalculationStatus(null);
        try {
            const response = await api.post(`/projects/${projectId}/calculate`);
            // The backend returns a status summary immediately
            setCalculationStatus(response.data.results);
            setTabIndex(2); // Switch to the calculation results tab
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
        return forest ? forest.forest_name : 'Unknown Forest';
    };

    if (loading) {
        return <CircularProgress />;
    }

    if (error) {
        return <Alert severity="error">{error}</Alert>;
    }

    if (!project) {
        return <Typography>Project not found.</Typography>;
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    {project.project_name}
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
                    <Tab label="Calculation Status" />
                </Tabs>
            </Box>

            {/* Overview Tab */}
            <Box hidden={tabIndex !== 0} sx={{ p: 3 }}>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6">Project Details</Typography>
                                <Typography>Status: {project.status}</Typography>
                                <Typography>Area: {project.area_ha || 'N/A'} ha</Typography>
                                <Typography>Created: {new Date(project.created_at).toLocaleDateString()}</Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Box>

            {/* Forests Tab */}
            <Box hidden={tabIndex !== 1} sx={{ p: 3 }}>
                <List>
                    {forests.map((forest) => (
                        <ListItem key={forest.forest_id} disablePadding>
                             <ListItemButton component={RouterLink} to={`/forests/${forest.forest_id}`}>
                                <ListItemText 
                                    primary={forest.forest_name} 
                                    secondary={`Type: ${forest.forest_type} | Area: ${forest.area_ha} ha`} 
                                />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            </Box>

            {/* Calculation Results Tab */}
            <Box hidden={tabIndex !== 2} sx={{ p: 3 }}>
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
        </Container>
    );
};

export default ProjectDetail;
