import React from 'react';
import { Link } from 'react-router-dom';
import useApi from '../../hooks/useApi';
import { Project } from '../../types';

const RecentForests: React.FC = () => {
    const { data: projects, error, isLoading } = useApi<Project[]>('/projects/?project_type=Forestry&limit=5');

    return (
        <div className="bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-2">Recent Forestry Projects</h2>
            {isLoading && <p>Loading...</p>}
            {error && <p className="text-red-500">Failed to fetch projects.</p>}
            <ul>
                {projects && projects.length > 0 ? (
                    projects.map((project) => (
                        <li key={project.id} className="p-2 hover:bg-gray-100 rounded">
                            <Link to={`/projects/${project.id}`} className="font-semibold text-blue-600">
                                {project.name}
                            </Link>
                        </li>
                    ))
                ) : (
                    !isLoading && <p>No forestry projects found.</p>
                )}
            </ul>
        </div>
    );
};

export default RecentForests; 