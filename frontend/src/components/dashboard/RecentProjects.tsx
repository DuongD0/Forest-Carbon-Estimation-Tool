import React from 'react';
import { Link } from 'react-router-dom';
import useApi from '../../hooks/useApi';
import { Project } from '../../types'; // Assuming Project type is defined in types.ts

const RecentProjects: React.FC = () => {
    const { data: projects, error, isLoading } = useApi<Project[]>('/projects/?limit=5');

    return (
        <div className="bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-2">Recent Projects</h2>
            {isLoading && <p>Loading...</p>}
            {error && <p className="text-red-500">Failed to fetch recent projects.</p>}
            <ul>
                {projects && projects.length > 0 ? (
                    projects.map((project) => (
                        <li key={project.id} className="p-2 hover:bg-gray-100 rounded">
                            <Link to={`/projects/${project.id}`} className="font-semibold text-blue-600">
                                {project.name}
                            </Link>
                            <p className="text-sm text-gray-600 truncate">{project.description}</p>
                        </li>
                    ))
                ) : (
                    !isLoading && <p>No recent projects found.</p>
                )}
            </ul>
        </div>
    );
};

export default RecentProjects; 