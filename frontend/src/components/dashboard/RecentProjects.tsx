import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Card, 
  CardHeader, 
  CardContent, 
  List, 
  ListItem, 
  ListItemText, 
  Typography, 
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import { projectService } from '../../services/api';

interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  project_type: string;
}

const RecentProjects: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const data = await projectService.getProjects();
                setProjects(data.slice(0, 5)); // Get first 5 projects
                setError(null);
            } catch (err: any) {
                console.error('Error fetching projects:', err);
                console.error('Error details:', {
                    message: err.message,
                    response: err.response?.data,
                    status: err.response?.status
                });
                // Check if it's a network error or CORS issue
                if (err.message === 'Network Error' && !err.response) {
                    setError(`Failed to fetch recent projects: Network Error - Check if backend is running and CORS is configured`);
                } else {
                    setError(`Failed to fetch recent projects: ${err.message || 'Unknown error'}`);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, []);

    return (
        <Card>
            <CardHeader title="Recent Projects" />
            <CardContent>
                {loading && (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                        <CircularProgress />
                    </div>
                )}
                {error && <Alert severity="error">{error}</Alert>}
                {!loading && !error && (
                    <List>
                        {projects.length > 0 ? (
                            projects.map((project) => (
                                <ListItem 
                                    key={project.id} 
                                    component={Link} 
                                    to={`/projects/${project.id}`}
                                    sx={{ 
                                        textDecoration: 'none', 
                                        color: 'inherit',
                                        '&:hover': { backgroundColor: 'action.hover' }
                                    }}
                                >
                                    <ListItemText
                                        primary={project.name}
                                        secondary={
                                            <div>
                                                <Typography variant="body2" color="text.secondary">
                                                    {project.description || 'No description available'}
                                                </Typography>
                                                <Chip 
                                                    label={project.status} 
                                                    size="small" 
                                                    color={project.status === 'Active' ? 'success' : 'default'}
                                                    sx={{ mt: 1 }}
                                                />
                                            </div>
                                        }
                                    />
                                </ListItem>
                            ))
                        ) : (
                            <Typography variant="body2" color="text.secondary">
                                No recent projects found.
                            </Typography>
                        )}
                    </List>
                )}
            </CardContent>
        </Card>
    );
};

export default RecentProjects; 