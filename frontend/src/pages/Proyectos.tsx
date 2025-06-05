import { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CardMedia,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assignment as AssignmentIcon,
  Person as PersonIcon,
  AttachMoney as MoneyIcon,
  CalendarToday as CalendarIcon,
  PhotoCamera as PhotoIcon,
} from '@mui/icons-material';
import { proyectosService, Proyecto, EstadoProyecto } from '../services/proyectos';
import { AxiosError } from 'axios';
import api from '../services/api';

const Proyectos = () => {
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingProyecto, setEditingProyecto] = useState<Proyecto | null>(null);
  const [formData, setFormData] = useState<Partial<Proyecto>>({
    nombre: '',
    descripcion: '',
    fecha_inicio: '',
    fecha_fin: '',
    estado: 'PLAN',
    presupuesto: 0,
    activo: true
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEstado, setSelectedEstado] = useState<EstadoProyecto | ''>('');
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  });

  const estados: EstadoProyecto[] = ['PLAN', 'EJE', 'SUS', 'COM', 'CAN'];

  useEffect(() => {
    loadProyectos();
  }, []);

  const loadProyectos = async () => {
    try {
      setLoading(true);
      setError(null); // Limpiar errores previos
      const data = await proyectosService.getAll();
      setProyectos(data);
    } catch (err) {
      console.error('Error al cargar proyectos:', err);
      if (err instanceof AxiosError) {
        if (err.response?.status === 401) {
          setError('No tienes autorización para ver los proyectos. Por favor, inicia sesión.');
        } else if (err.response?.status === 404) {
          setError('No se encontraron proyectos.');
        } else if (err.response?.data) {
          setError(`Error al cargar los proyectos: ${JSON.stringify(err.response.data)}`);
        } else {
          setError('Error al cargar los proyectos. Por favor, verifica tu conexión.');
        }
      } else {
        setError('Error inesperado al cargar los proyectos.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      setLoading(true);
      let data: Proyecto[] = [];

      const params = new URLSearchParams();
      
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      if (selectedEstado) {
        params.append('estado', selectedEstado);
      }
      if (dateRange.startDate) {
        params.append('fecha_inicio', dateRange.startDate);
      }
      if (dateRange.endDate) {
        params.append('fecha_fin', dateRange.endDate);
      }

      const response = await api.get<Proyecto[]>(`/api/proyectos/?${params.toString()}`);
      data = response.data;
      setProyectos(data);
    } catch (err) {
      console.error('Error al buscar proyectos:', err);
      setError('Error al buscar proyectos');
    } finally {
      setLoading(false);
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedEstado('');
    setDateRange({ startDate: '', endDate: '' });
    loadProyectos();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleOpenDialog = (proyecto?: Proyecto) => {
    if (proyecto) {
      setEditingProyecto(proyecto);
      setFormData({
        ...proyecto,
        fecha_inicio: proyecto.fecha_inicio ? new Date(proyecto.fecha_inicio).toISOString().split('T')[0] : '',
        fecha_fin: proyecto.fecha_fin ? new Date(proyecto.fecha_fin).toISOString().split('T')[0] : ''
      });
      setPreviewUrl(proyecto.foto_url || null);
      setSelectedFile(null);
    } else {
      setEditingProyecto(null);
      setFormData({
        nombre: '',
        descripcion: '',
        fecha_inicio: '',
        fecha_fin: '',
        estado: 'PLAN',
        presupuesto: 0,
        activo: true
      });
      setPreviewUrl(null);
      setSelectedFile(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingProyecto(null);
    setFormData({
      nombre: '',
      descripcion: '',
      fecha_inicio: '',
      fecha_fin: '',
      estado: 'PLAN',
      presupuesto: 0,
      activo: true
    });
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  const handleSubmit = async () => {
    try {
      // Validaciones mejoradas
      const errors: string[] = [];
      if (!formData.nombre?.trim()) {
        errors.push('El nombre del proyecto es requerido');
      }
      if (!formData.fecha_inicio) {
        errors.push('La fecha de inicio es requerida');
      }
      if (formData.fecha_fin && new Date(formData.fecha_fin) < new Date(formData.fecha_inicio)) {
        errors.push('La fecha de fin no puede ser anterior a la fecha de inicio');
      }
      if (formData.presupuesto < 0) {
        errors.push('El presupuesto no puede ser negativo');
      }

      if (errors.length > 0) {
        setError(errors.join('\n'));
        return;
      }

      const dataToSend = {
        ...formData,
        fecha_inicio: formData.fecha_inicio ? new Date(formData.fecha_inicio).toISOString().split('T')[0] : null,
        fecha_fin: formData.fecha_fin ? new Date(formData.fecha_fin).toISOString().split('T')[0] : null,
        presupuesto: Number(formData.presupuesto) || 0,
        estado: formData.estado || 'PLAN',
        foto: selectedFile
      };

      if (editingProyecto) {
        await proyectosService.update(editingProyecto.id, dataToSend);
      } else {
        await proyectosService.create(dataToSend as Omit<Proyecto, 'id'>);
      }

      handleCloseDialog();
      await loadProyectos();
      setError(null); // Limpiar errores al tener éxito
    } catch (err) {
      console.error('Error al guardar proyecto:', err);
      if (err instanceof AxiosError && err.response?.data) {
        const errorData = err.response.data;
        if (typeof errorData === 'object') {
          const errorMessages = Object.entries(errorData)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n');
          setError(`Error al guardar el proyecto:\n${errorMessages}`);
        } else {
          setError(`Error al guardar el proyecto: ${errorData}`);
        }
      } else {
        setError('Error al guardar el proyecto. Por favor, intente nuevamente.');
      }
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Está seguro que desea eliminar este proyecto?')) {
      try {
        await proyectosService.delete(id);
        await loadProyectos();
      } catch (err) {
        console.error('Error al eliminar proyecto:', err);
        if (err instanceof AxiosError && err.response?.data) {
          setError(`Error al eliminar el proyecto: ${JSON.stringify(err.response.data)}`);
        } else {
          setError('Error al eliminar el proyecto');
        }
      }
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'EJE':
        return 'success';
      case 'PLAN':
      case 'SUS':
        return 'warning';
      case 'COM':
        return 'info';
      case 'CAN':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
        <Button variant="contained" onClick={loadProyectos}>
          Reintentar
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Proyectos
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Nuevo Proyecto
        </Button>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Buscar"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Buscar por nombre o descripción"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              select
              label="Estado"
              value={selectedEstado}
              onChange={(e) => setSelectedEstado(e.target.value as EstadoProyecto)}
            >
              <MenuItem value="">Todos</MenuItem>
              {estados.map((estado) => (
                <MenuItem key={estado} value={estado}>
                  {proyectosService.getEstadoDisplay(estado)}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField
              fullWidth
              type="date"
              label="Fecha Inicio"
              value={dateRange.startDate}
              onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField
              fullWidth
              type="date"
              label="Fecha Fin"
              value={dateRange.endDate}
              onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={1}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
            >
              Buscar
            </Button>
          </Grid>
        </Grid>
        <Box sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            onClick={handleResetFilters}
          >
            Limpiar Filtros
          </Button>
        </Box>
      </Box>

      {proyectos.length === 0 ? (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="textSecondary">
            No hay proyectos registrados
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {proyectos.map((proyecto) => (
            <Grid item xs={12} sm={6} md={4} key={proyecto.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {proyecto.foto_url && (
                  <CardMedia
                    component="img"
                    height="140"
                    image={proyecto.foto_url}
                    alt={proyecto.nombre}
                  />
                )}
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {proyecto.nombre}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {proyecto.descripcion}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    <Chip
                      icon={<CalendarIcon />}
                      label={`Inicio: ${new Date(proyecto.fecha_inicio).toLocaleDateString()}`}
                      size="small"
                    />
                    {proyecto.fecha_fin && (
                      <Chip
                        icon={<CalendarIcon />}
                        label={`Fin: ${new Date(proyecto.fecha_fin).toLocaleDateString()}`}
                        size="small"
                      />
                    )}
                    <Chip
                      icon={<MoneyIcon />}
                      label={`Presupuesto: $${proyecto.presupuesto.toLocaleString()}`}
                      size="small"
                    />
                    <Chip
                      label={proyectosService.getEstadoDisplay(proyecto.estado)}
                      color={getEstadoColor(proyecto.estado)}
                      size="small"
                    />
                  </Box>
                  {proyecto.responsable_info && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <PersonIcon sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        Responsable: {proyecto.responsable_info.nombre}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(proyecto)}
                    title="Editar"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(proyecto.id)}
                    title="Eliminar"
                  >
                    <DeleteIcon />
                  </IconButton>
                  <Button
                    size="small"
                    startIcon={<AssignmentIcon />}
                    onClick={() => {/* TODO: Implementar vista de detalles */}}
                  >
                    Ver Detalles
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingProyecto ? 'Editar Proyecto' : 'Nuevo Proyecto'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Descripción"
                  value={formData.descripcion}
                  onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                  multiline
                  rows={4}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Fecha de Inicio"
                  value={formData.fecha_inicio}
                  onChange={(e) => setFormData({ ...formData, fecha_inicio: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Fecha de Finalización"
                  value={formData.fecha_fin || ''}
                  onChange={(e) => setFormData({ ...formData, fecha_fin: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Estado"
                  value={formData.estado}
                  onChange={(e) => setFormData({ ...formData, estado: e.target.value as EstadoProyecto })}
                >
                  {estados.map((estado) => (
                    <MenuItem key={estado} value={estado}>
                      {proyectosService.getEstadoDisplay(estado)}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Presupuesto"
                  value={formData.presupuesto}
                  onChange={(e) => setFormData({ ...formData, presupuesto: Number(e.target.value) })}
                  InputProps={{
                    startAdornment: '$',
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<PhotoIcon />}
                  >
                    {previewUrl ? 'Cambiar Foto' : 'Subir Foto'}
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleFileChange}
                    />
                  </Button>
                  {previewUrl && (
                    <Box
                      component="img"
                      src={previewUrl}
                      alt="Preview"
                      sx={{
                        width: 100,
                        height: 100,
                        objectFit: 'cover',
                        borderRadius: 1,
                      }}
                    />
                  )}
                </Box>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingProyecto ? 'Guardar Cambios' : 'Crear Proyecto'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Proyectos;
