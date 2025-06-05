import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Chip,
  Grid,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  AccessTime as AccessTimeIcon,
  CheckCircle as CheckCircleIcon,
  LocationOn as LocationIcon,
  
} from '@mui/icons-material';
import { asistenciaService } from '../services/asistencia';
import type { Asistencia } from '../services/asistencia';
import { useSnackbar } from 'notistack';
import { AxiosError } from 'axios';

const Asistencia = () => {
  const navigate = useNavigate();
  const [asistencias, setAsistencias] = useState<Asistencia[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [tipoRegistro, setTipoRegistro] = useState<'ENT' | 'SAL'>('ENT');
  const [ubicacion, setUbicacion] = useState('');
  const [observaciones, setObservaciones] = useState('');
  const { enqueueSnackbar } = useSnackbar();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Verificar autenticación
    const token = localStorage.getItem('token');
    if (!token) {
      enqueueSnackbar('Debe iniciar sesión para acceder a esta función', { variant: 'error' });
      navigate('/login');
      return;
    }
    cargarAsistencias();
  }, [navigate, enqueueSnackbar]);

  const cargarAsistencias = async () => {
    try {
      setLoading(true);
      const data = await asistenciaService.getAll();
      setAsistencias(data);
    } catch (error) {
      console.error('Error al cargar asistencias:', error);
      enqueueSnackbar('Error al cargar las asistencias', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleRegistrarAsistencia = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Obtener el token de autenticación
      const token = localStorage.getItem('token');
      if (!token) {
        enqueueSnackbar('Sesión expirada. Por favor, inicie sesión nuevamente.', { variant: 'error' });
        navigate('/login');
        return;
      }

      const now = new Date();
      const dataToSend = {
        tipo: tipoRegistro,
        ubicacion: ubicacion || undefined,
        observaciones: observaciones || undefined,
        fecha: now.toISOString().split('T')[0],
        hora: now.toTimeString().split(' ')[0]
      };

      console.log('Enviando datos:', dataToSend);

      const response = await asistenciaService.create(dataToSend);
      
      if (response) {
        enqueueSnackbar('Asistencia registrada exitosamente', { variant: 'success' });
        setOpenDialog(false);
        setError(null);
        // Limpiar el formulario
        setTipoRegistro('ENT');
        setUbicacion('');
        setObservaciones('');
        // Recargar la lista de asistencias
        await cargarAsistencias();
      }
    } catch (err) {
      console.error('Error al registrar asistencia:', err);
      if (err instanceof AxiosError) {
        if (err.response?.status === 401) {
          enqueueSnackbar('Sesión expirada. Por favor, inicie sesión nuevamente.', { variant: 'error' });
          navigate('/login');
          return;
        }
        
        if (err.response?.data) {
          const errorData = err.response.data;
          if (typeof errorData === 'object') {
            const errorMessages = Object.entries(errorData)
              .map(([key, value]) => `${key}: ${value}`)
              .join('\n');
            setError(`Error al registrar la asistencia:\n${errorMessages}`);
            enqueueSnackbar(`Error al registrar la asistencia: ${errorMessages}`, { variant: 'error' });
          } else {
            setError(`Error al registrar la asistencia: ${errorData}`);
            enqueueSnackbar(`Error al registrar la asistencia: ${errorData}`, { variant: 'error' });
          }
        }
      } else {
        setError('Error al registrar la asistencia');
        enqueueSnackbar('Error al registrar la asistencia', { variant: 'error' });
      }
    } finally {
      setLoading(false);
    }
  };

  const getEstadoColor = (tipo: string) => {
    switch (tipo) {
      case 'ENT':
        return 'success';
      case 'SAL':
        return 'info';
      default:
        return 'default';
    }
  };

  const getEstadoIcon = (tipo: string) => {
    switch (tipo) {
      case 'ENT':
        return <CheckCircleIcon />;
      case 'SAL':
        return <AccessTimeIcon />;
      default:
        return null;
    }
  };

  const asistenciasFiltradas = asistencias.filter(asistencia =>
    `${asistencia.usuario.first_name} ${asistencia.usuario.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const validateForm = () => {
    // Validar que el tipo de registro esté seleccionado
    if (!tipoRegistro) {
      setError('Por favor seleccione un tipo de registro');
      return false;
    }
    return true;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Asistencia</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ borderRadius: 2 }}
          onClick={() => setOpenDialog(true)}
        >
          Registrar Asistencia
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Entradas</Typography>
              </Box>
              <Typography variant="h4">
                {asistencias.filter(a => a.tipo === 'ENT').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AccessTimeIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Salidas</Typography>
              </Box>
              <Typography variant="h4">
                {asistencias.filter(a => a.tipo === 'SAL').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Buscar empleado..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper} sx={{ boxShadow: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Empleado</TableCell>
                <TableCell>Fecha</TableCell>
                <TableCell>Hora</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Ubicación</TableCell>
                <TableCell>Observaciones</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {asistenciasFiltradas.map((asistencia) => (
                <TableRow key={asistencia.id}>
                  <TableCell>{`${asistencia.usuario.first_name} ${asistencia.usuario.last_name}`}</TableCell>
                  <TableCell>{new Date(asistencia.fecha).toLocaleDateString()}</TableCell>
                  <TableCell>{asistencia.hora}</TableCell>
                  <TableCell>
                    <Chip
                      icon={getEstadoIcon(asistencia.tipo)}
                      label={asistencia.tipo === 'ENT' ? 'Entrada' : 'Salida'}
                      color={getEstadoColor(asistencia.tipo) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {asistencia.ubicacion && (
                      <Chip
                        icon={<LocationIcon />}
                        label={asistencia.ubicacion}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </TableCell>
                  <TableCell>{asistencia.observaciones}</TableCell>
                  <TableCell>
                    <IconButton color="primary" size="small">
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Registrar Asistencia</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Tipo de Registro</InputLabel>
              <Select
                value={tipoRegistro}
                label="Tipo de Registro"
                onChange={(e) => setTipoRegistro(e.target.value as 'ENT' | 'SAL')}
              >
                <MenuItem value="ENT">Entrada</MenuItem>
                <MenuItem value="SAL">Salida</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Ubicación"
              value={ubicacion}
              onChange={(e) => setUbicacion(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Observaciones"
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              multiline
              rows={3}
            />
            {error && (
              <Typography color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpenDialog(false);
            setError(null);
            setTipoRegistro('ENT');
            setUbicacion('');
            setObservaciones('');
          }}>
            Cancelar
          </Button>
          <Button 
            onClick={handleRegistrarAsistencia} 
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Registrar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Asistencia; 