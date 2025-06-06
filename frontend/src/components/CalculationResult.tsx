import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Alert
} from '@mui/material';

// Duplicating types for now, ideally these would be in a shared types file
interface CarbonCreditResult {
  gross_credits_co2e: number;
  net_credits_co2e: number;
  issuable_credits_co2e: number;
  leakage_deduction_co2e: number;
  permanence_buffer_co2e: number;
}

interface CarbonStockResult {
  agb_carbon_tonnes: number;
  bgb_carbon_tonnes: number;
  total_carbon_tonnes: number;
  total_co2e_tonnes: number;
}

interface ForestCalculationResult {
  forest_id: number;
  current_stock: CarbonStockResult;
  baseline_stock: { total_co2e_tonnes: number };
  carbon_credits: CarbonCreditResult;
  error?: string;
}

interface ProjectCalculationResult {
  project_id: number;
  forest_calculations: ForestCalculationResult[];
}

interface Forest {
    id: number;
    name: string;
}

interface CalculationResultProps {
  results: ProjectCalculationResult;
  forests: Forest[];
}

const CalculationResult: React.FC<CalculationResultProps> = ({ results, forests }) => {
  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h5" gutterBottom>
        Calculation Results for Project {results.project_id}
      </Typography>
      {results.forest_calculations.map((forestResult) => (
        <Card key={forestResult.forest_id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">
              Forest: {forests.find(f => f.id === forestResult.forest_id)?.name || `ID: ${forestResult.forest_id}`}
            </Typography>
            {forestResult.error ? (
              <Alert severity="warning">Could not process this forest: {forestResult.error}</Alert>
            ) : (
                <Box sx={{ display: 'flex', flexDirection: 'row', mt: 1 }}>
                    <Box sx={{ width: '50%', pr: 1 }}>
                        <Typography variant="subtitle1" gutterBottom>Carbon Stock (tCO2e)</Typography>
                        <List dense>
                        <ListItem>
                            <ListItemText primary="Total CO2e" secondary={`${forestResult.current_stock.total_co2e_tonnes.toFixed(2)} tCO2e`} />
                        </ListItem>
                        <ListItem>
                            <ListItemText primary="Baseline" secondary={`${forestResult.baseline_stock.total_co2e_tonnes.toFixed(2)} tCO2e`} />
                        </ListItem>
                        </List>
                    </Box>
                    <Box sx={{ width: '50%', pl: 1 }}>
                        <Typography variant="subtitle1" gutterBottom>Carbon Credits (tCO2e)</Typography>
                        <List dense>
                        <ListItem>
                            <ListItemText 
                            primary="Issuable Credits" 
                            secondary={
                                <Typography color="primary" variant="body2" sx={{ fontWeight: 'bold' }}>
                                {forestResult.carbon_credits.issuable_credits_co2e.toFixed(2)}
                                </Typography>
                            } 
                            />
                        </ListItem>
                        <ListItem>
                            <ListItemText primary="Gross Reduction" secondary={`${forestResult.carbon_credits.gross_credits_co2e.toFixed(2)}`} />
                        </ListItem>
                        <ListItem>
                            <ListItemText primary="Leakage Deduction" secondary={`-${forestResult.carbon_credits.leakage_deduction_co2e.toFixed(2)}`} />
                        </ListItem>
                        <ListItem>
                            <ListItemText primary="Permanence Buffer" secondary={`-${forestResult.carbon_credits.permanence_buffer_co2e.toFixed(2)}`} />
                        </ListItem>
                        </List>
                    </Box>
                </Box>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default CalculationResult; 