import React from 'react';
import RecentProjects from '../components/dashboard/RecentProjects';
import RecentForests from '../components/dashboard/RecentForests';
// import CarbonSummary from '../components/dashboard/CarbonSummary';

const Dashboard: React.FC = () => {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <RecentProjects />
                <RecentForests />
                {/* TODO: Re-enable this components once they are created */}
                {/* <CarbonSummary /> */}
            </div>
        </div>
    );
};

export default Dashboard;
