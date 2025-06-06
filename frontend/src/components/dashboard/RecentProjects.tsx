import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

interface Project {
    project_id: number;
    project_name: string;
    description: string;
}

const RecentProjects: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const response = await api.get('/projects/?limit=5');
                setProjects(response.data);
            } catch (err) {
                setError('Failed to fetch recent projects.');
                console.error(err);
            }
        };

        fetchProjects();
    }, []);

    return (
        <div className="bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-2">Recent Projects</h2>
            {error && <p className="text-red-500">{error}</p>}
            <ul>
                {projects.length > 0 ? (
                    projects.map((project) => (
                        <li key={project.project_id} className="p-2 hover:bg-gray-100 rounded">
                            <Link to={`/projects/${project.project_id}`} className="font-semibold text-blue-600">
                                {project.project_name}
                            </Link>
                            <p className="text-sm text-gray-600 truncate">{project.description}</p>
                        </li>
                    ))
                ) : (
                    <p>No recent projects found.</p>
                )}
            </ul>
        </div>
    );
};

export default RecentProjects; 