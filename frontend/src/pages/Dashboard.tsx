import { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, CircularProgress, Alert } from '@mui/material';
import { 
  Assignment as AssignmentIcon,
  Construction as ConstructionIcon,
  Inventory as InventoryIcon,
  People as PeopleIcon
} from '@mui/icons-material';

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    proyectosActivos: 3,
    materialesEnStock: 24,
    empleadosActivos: 12
  });

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <Alert severity="error">{error}</Alert>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                <AssignmentIcon color="primary" style={{ marginRight: '10px' }} />
                <Typography variant="h6">Proyectos en Ejecución</Typography>
              </div>
              <Typography variant="h4">{stats.proyectosActivos}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                <InventoryIcon color="primary" style={{ marginRight: '10px' }} />
                <Typography variant="h6">Materiales en Stock</Typography>
              </div>
              <Typography variant="h4">{stats.materialesEnStock}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                <PeopleIcon color="primary" style={{ marginRight: '10px' }} />
                <Typography variant="h6">Empleados Activos</Typography>
              </div>
              <Typography variant="h4">{stats.empleadosActivos}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard; 