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

const RecentForests: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const data = await projectService.getProjects();
                // Filter for forestry projects and get first 5
                const forestryProjects = data.filter((p: Project) => p.project_type === 'Forestry').slice(0, 5);
                setProjects(forestryProjects);
            } catch (err) {
                setError('Failed to fetch forestry projects');
                console.error('Error fetching projects:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, []);

    return (
        <Card>
            <CardHeader title="Recent Forestry Projects" />
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
                                            <Chip 
                                                label={project.status} 
                                                size="small" 
                                                color={project.status === 'Active' ? 'success' : 'default'}
                                                sx={{ mt: 1 }}
                                            />
                                        }
                                    />
                                </ListItem>
                            ))
                        ) : (
                            <Typography variant="body2" color="text.secondary">
                                No forestry projects found.
                            </Typography>
                        )}
                    </List>
                )}
            </CardContent>
        </Card>
    );
};

export default RecentForests; 