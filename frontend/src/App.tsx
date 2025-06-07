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

interface PrivateRouteProps {
  children: JSX.Element;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
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
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/projects"
              element={
                <PrivateRoute>
                  <ProjectList />
                </PrivateRoute>
              }
            />
            <Route
              path="/projects/:projectId"
              element={
                <PrivateRoute>
                  <ProjectDetail />
                </PrivateRoute>
              }
            />
            <Route
              path="/forests/:forestId"
              element={
                <PrivateRoute>
                  <ForestDetail />
                </PrivateRoute>
              }
            />
            <Route
              path="/imagery/:imageryId"
              element={
                <PrivateRoute>
                  <ImageryDetail />
                </PrivateRoute>
              }
            />
            <Route
              path="/calculate-carbon"
              element={
                <PrivateRoute>
                  <CarbonCalculation />
                </PrivateRoute>
              }
            />
            {/* Redirect root to dashboard if authenticated */}
            <Route path="/" element={<Navigate to="/" />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
};

export default App;
