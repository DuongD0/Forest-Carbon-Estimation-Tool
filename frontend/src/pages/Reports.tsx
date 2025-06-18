import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';

const Reports: React.FC = () => {
  // Mock data for demonstration
  const carbonData = [
    { project: 'Forest Project A', credits: 1250, status: 'Active' },
    { project: 'Forest Project B', credits: 890, status: 'Completed' },
    { project: 'Forest Project C', credits: 2100, status: 'Active' },
  ];

  const totalCredits = carbonData.reduce((sum, project) => sum + project.credits, 0);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Carbon Credit Reports
      </Typography>
      
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Total Credits Issued" />
            <CardContent>
              <Typography variant="h3" color="primary">
                {totalCredits.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                CO2e tons
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Active Projects" />
            <CardContent>
              <Typography variant="h3" color="success.main">
                {carbonData.filter(p => p.status === 'Active').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Projects
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Average Credits per Project" />
            <CardContent>
              <Typography variant="h3" color="info.main">
                {Math.round(totalCredits / carbonData.length).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                CO2e tons
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Detailed Table */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Project Details" />
            <CardContent>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Project Name</TableCell>
                      <TableCell align="right">Credits Issued</TableCell>
                      <TableCell align="center">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {carbonData.map((project, index) => (
                      <TableRow key={index}>
                        <TableCell component="th" scope="row">
                          {project.project}
                        </TableCell>
                        <TableCell align="right">
                          {project.credits.toLocaleString()} CO2e tons
                        </TableCell>
                        <TableCell align="center">
                          <Typography 
                            variant="body2" 
                            color={project.status === 'Active' ? 'success.main' : 'text.secondary'}
                          >
                            {project.status}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Reports;