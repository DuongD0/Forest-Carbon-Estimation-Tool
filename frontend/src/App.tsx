import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ProjectList from "./pages/ProjectList";
import ProjectDetail from "./pages/ProjectDetail";
import ForestDetail from "./pages/ForestDetail";
import ImageryDetail from "./pages/ImageryDetail";
import CarbonCalculation from "./pages/CarbonCalculation";
import Marketplace from "./pages/Marketplace";
import Reports from "./pages/Reports";
import ImageUploadPage from "./pages/ImageUploadPage";

interface PrivateRouteProps {
  component: React.ComponentType;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ component: Component }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <Component />;
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={<PrivateRoute component={Dashboard} />}
            />
            <Route
              path="/projects"
              element={<PrivateRoute component={ProjectList} />}
            />
            <Route
              path="/projects/:projectId"
              element={<PrivateRoute component={ProjectDetail} />}
            />
            <Route
              path="/reports"
              element={<PrivateRoute component={Reports} />}
            />
            <Route
              path="/forests/:forestId"
              element={<PrivateRoute component={ForestDetail} />}
            />
            <Route
              path="/imagery/:imageryId"
              element={<PrivateRoute component={ImageryDetail} />}
            />
            <Route
              path="/calculate-carbon"
              element={<PrivateRoute component={CarbonCalculation} />}
            />
            <Route
              path="/marketplace"
              element={<PrivateRoute component={Marketplace} />}
            />
            <Route
              path="/upload-images"
              element={<PrivateRoute component={ImageUploadPage} />}
            />
            {/* redirect to dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
};

export default App;
