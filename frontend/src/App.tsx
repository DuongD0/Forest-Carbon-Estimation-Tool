import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { withAuthenticationRequired } from "@auth0/auth0-react";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ProjectList from "./pages/ProjectList";
import ProjectDetail from "./pages/ProjectDetail";
import ForestDetail from "./pages/ForestDetail";
import ImageryDetail from "./pages/ImageryDetail";
import CarbonCalculation from "./pages/CarbonCalculation";
import Marketplace from "./pages/Marketplace";

interface PrivateRouteProps {
  component: React.ComponentType;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ component }) => {
  const Component = withAuthenticationRequired(component, {
    // You can add a custom loading component here
  });
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
            {/* Redirect root to dashboard */}
            <Route path="/" element={<Navigate to="/" />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
};

export default App;
