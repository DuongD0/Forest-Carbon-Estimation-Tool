import React from 'react';

const RecentForests: React.FC = () => {
    return (
        <div className="bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-2">Recent Forests</h2>
            {/* Placeholder content */}
            <ul>
                <li className="p-2 hover:bg-gray-100 rounded">Vietnam Tropical Forest</li>
                <li className="p-2 hover:bg-gray-100 rounded">Mekong Delta Mangrove</li>
                <li className="p-2 hover:bg-gray-100 rounded">Bamboo Forest Reserve</li>
            </ul>
        </div>
    );
};

export default RecentForests; 