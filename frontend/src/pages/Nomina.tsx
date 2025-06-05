import { useState, useEffect } from 'react';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  SelectChangeEvent,
  FormHelperText,
  Container,
  CircularProgress,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Payment as PaymentIcon,
  AttachMoney as AttachMoneyIcon,
  AccountBalance as AccountBalanceIcon,
  FilterList as FilterListIcon,
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { nominaService, type NominaResponse, type NominaEstado } from '../services/nomina';
import { useSnackbar } from 'notistack';

// Definición de tipo para los empleados disponibles
type Empleado = {
  id: number;
  nombre: string;
};

// Definición del tipo para el formulario de nómina
type NominaFormData = {
  id: number;
  empleado_id: number;
  empleado: string;
  periodo: string;
  dias_trabajados: number;
  sueldo_base: number;
  horas_extras: number;
  bonificaciones: number;
  deducciones: number;
  total: number;
  estado: NominaEstado;
};

const Nomina = () => {
  const [nominas, setNominas] = useState<NominaResponse[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const [filtroPeriodo, setFiltroPeriodo] = useState('');
  const [filtroEmpleado, setFiltroEmpleado] = useState('');
  const [openDetalleDialog, setOpenDetalleDialog] = useState(false);
  const [nominaSeleccionada, setNominaSeleccionada] = useState<NominaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Lista de empleados disponibles (podría venir de una API)
  const empleados: Empleado[] = [
    { id: 1, nombre: 'Juan Pérez' },
    { id: 2, nombre: 'María García' },
    { id: 3, nombre: 'Carlos López' }
  ];

  const [formData, setFormData] = useState<NominaFormData>({
    id: 0,
    empleado_id: 1,
    empleado: '',
    periodo: '',
    dias_trabajados: 0,
    sueldo_base: 0,
    horas_extras: 0,
    bonificaciones: 0,
    deducciones: 0,
    total: 0,
    estado: 'Pendiente',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const inicializarDatos = async () => {
      try {
        setLoading(true);
        setError(null);
        await cargarNominas();
      } catch (error: any) {
        console.error('Error al inicializar datos:', error);
        setError(error.message || 'Error al cargar los datos. Por favor, intente nuevamente.');
        enqueueSnackbar('Error al cargar los datos', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };

    inicializarDatos();
  }, [enqueueSnackbar]);

  const cargarNominas = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        window.location.href = '/login';
        return;
      }
      const data = await nominaService.getAll();
      setNominas(data || []);
    } catch (error: any) {
      console.error('Error al cargar las nóminas:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Error al cargar las nóminas';
      setError(errorMessage);
      setNominas([]);
      enqueueSnackbar(errorMessage, { 
        variant: 'error',
        autoHideDuration: 5000,
        anchorOrigin: {
          vertical: 'top',
          horizontal: 'center'
        }
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.empleado_id) {
      newErrors.empleado_id = 'Debe seleccionar un empleado';
    }

    if (!formData.periodo) {
      newErrors.periodo = 'El período es requerido';
    } else if (!/^\d{4}-\d{2}$/.test(formData.periodo)) {
      newErrors.periodo = 'El período debe tener el formato YYYY-MM';
    }

    if (formData.dias_trabajados <= 0) {
      newErrors.dias_trabajados = 'Los días trabajados deben ser mayores a 0';
    } else if (formData.dias_trabajados > 31) {
      newErrors.dias_trabajados = 'Los días trabajados no pueden ser mayores a 31';
    }

    if (formData.sueldo_base <= 0) {
      newErrors.sueldo_base = 'El sueldo base debe ser mayor a 0';
    }

    if (formData.horas_extras < 0) {
      newErrors.horas_extras = 'Las horas extras no pueden ser negativas';
    }

    if (formData.bonificaciones < 0) {
      newErrors.bonificaciones = 'Las bonificaciones no pueden ser negativas';
    }

    if (formData.deducciones < 0) {
      newErrors.deducciones = 'Las deducciones no pueden ser negativas';
    }

    const total = calcularTotal();
    if (total < 0) {
      newErrors.total = 'El total no puede ser negativo';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // Asegurarse de que todos los campos numéricos sean números
      const payload = {
        empleado_id: Number(formData.empleado_id),
        periodo: formData.periodo,
        dias_trabajados: Number(formData.dias_trabajados),
        sueldo_base: Number(formData.sueldo_base),
        horas_extras: Number(formData.horas_extras || 0),
        bonificaciones: Number(formData.bonificaciones || 0),
        deducciones: Number(formData.deducciones || 0)
      };

      console.log('Enviando datos:', payload); // Para debugging

      if (editMode) {
        await nominaService.update(formData.id, { ...payload, estado: formData.estado });
        enqueueSnackbar('Nómina actualizada exitosamente', { variant: 'success' });
      } else {
        const response = await nominaService.create(payload);
        console.log('Respuesta del servidor:', response); // Para debugging
        enqueueSnackbar('Nómina creada exitosamente', { variant: 'success' });
      }
      
      resetForm();
      setOpenDialog(false);
      await cargarNominas();
    } catch (error: any) {
      console.error('Error al procesar la nómina:', error);
      let errorMessage = 'Error al procesar la nómina';
      
      if (error.response?.data) {
        // Si hay errores específicos del backend
        if (typeof error.response.data === 'object') {
          const backendErrors = error.response.data;
          errorMessage = 'Errores de validación:\n';
          for (const [field, errors] of Object.entries(backendErrors)) {
            errorMessage += `${field}: ${(errors as string[]).join(', ')}\n`;
          }
        } else {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      enqueueSnackbar(errorMessage, { 
        variant: 'error',
        autoHideDuration: 5000,
        anchorOrigin: {
          vertical: 'top',
          horizontal: 'center'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const numValue = ['dias_trabajados', 'sueldo_base', 'horas_extras', 'bonificaciones', 'deducciones'].includes(name)
      ? parseFloat(value) || 0
      : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: numValue
    }));

    // Limpiar error del campo cuando se modifica
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleEmpleadoChange = (e: SelectChangeEvent) => {
    const empleadoId = parseInt(e.target.value);
    const empleadoSeleccionado = empleados.find(e => e.id === empleadoId);
    
    if (empleadoSeleccionado) {
      setFormData(prev => ({
        ...prev,
        empleado_id: empleadoId,
        empleado: empleadoSeleccionado.nombre
      }));
    }
  };

  const calcularTotal = () => {
    const { sueldo_base, horas_extras, bonificaciones, deducciones } = formData;
    const valorHoraNormal = sueldo_base / (30 * 8);
    const valorHorasExtras = horas_extras * valorHoraNormal * 1.5;
    return sueldo_base + valorHorasExtras + bonificaciones - deducciones;
  };

  const resetForm = () => {
    setFormData({
      id: 0,
      empleado_id: 1,
      empleado: '',
      periodo: '',
      dias_trabajados: 0,
      sueldo_base: 0,
      horas_extras: 0,
      bonificaciones: 0,
      deducciones: 0,
      total: 0,
      estado: 'Pendiente',
    });
    setEditMode(false);
  };

  const handleEditar = (nomina: NominaResponse) => {
    setFormData({
      id: nomina.id,
      empleado_id: nomina.empleado_id,
      empleado: nomina.empleado,
      periodo: nomina.periodo,
      dias_trabajados: nomina.dias_trabajados,
      sueldo_base: nomina.sueldo_base,
      horas_extras: nomina.horas_extras,
      bonificaciones: nomina.bonificaciones,
      deducciones: nomina.deducciones,
      total: nomina.total,
      estado: nomina.estado,
    });
    setEditMode(true);
    setOpenDialog(true);
  };

  const handleEliminar = async (id: number) => {
    if (window.confirm('¿Está seguro de eliminar esta nómina?')) {
      try {
        setLoading(true);
        await nominaService.delete(id);
        enqueueSnackbar('Nómina eliminada exitosamente', { variant: 'success' });
        cargarNominas();
      } catch (error) {
        enqueueSnackbar('Error al eliminar la nómina', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    }
  };

  const handleMarcarComoPagada = async (id: number) => {
    try {
      setLoading(true);
      const nomina = nominas.find(n => n.id === id);
      if (nomina) {
        await nominaService.update(id, { 
          ...nomina, 
          estado: 'Pagado' 
        });
        enqueueSnackbar('Nómina marcada como pagada', { variant: 'success' });
        cargarNominas();
      }
    } catch (error) {
      enqueueSnackbar('Error al actualizar el estado de la nómina', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'Pagado': return 'success';
      case 'Pendiente': return 'warning';
      case 'Cancelado': return 'error';
      default: return 'default';
    }
  };

  const handleFiltrar = async () => {
    try {
      setLoading(true);
      let data: NominaResponse[] = [];
      
      if (filtroPeriodo) {
        data = await nominaService.getByPeriodo(filtroPeriodo);
      } else if (filtroEmpleado) {
        data = await nominaService.getByEmpleado(parseInt(filtroEmpleado));
      } else {
        data = await nominaService.getAll();
      }
      
      setNominas(data);
    } catch (error) {
      console.error('Error al filtrar nóminas:', error);
      enqueueSnackbar('Error al filtrar nóminas', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleExportarPDF = async (nomina: NominaResponse) => {
    try {
      // Aquí iría la lógica para exportar a PDF
      enqueueSnackbar('Exportando a PDF...', { variant: 'info' });
    } catch (error) {
      enqueueSnackbar('Error al exportar a PDF', { variant: 'error' });
    }
  };

  const handleExportarExcel = async () => {
    try {
      // Aquí iría la lógica para exportar a Excel
      enqueueSnackbar('Exportando a Excel...', { variant: 'info' });
    } catch (error) {
      enqueueSnackbar('Error al exportar a Excel', { variant: 'error' });
    }
  };

  const handleVerDetalle = (nomina: NominaResponse) => {
    setNominaSeleccionada(nomina);
    setOpenDetalleDialog(true);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gestión de Nóminas
        </Typography>

        {error ? (
          <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'error.light' }}>
            <Typography color="error">{error}</Typography>
            <Button 
              variant="contained" 
              onClick={() => window.location.reload()}
              sx={{ mt: 2 }}
            >
              Reintentar
            </Button>
          </Paper>
        ) : loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Filtros */}
            <Paper sx={{ p: 2, mb: 2 }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Período (YYYY-MM)"
                    value={filtroPeriodo}
                    onChange={(e) => setFiltroPeriodo(e.target.value)}
                    placeholder="2024-03"
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth>
                    <InputLabel>Empleado</InputLabel>
                    <Select
                      value={filtroEmpleado}
                      onChange={(e) => setFiltroEmpleado(e.target.value)}
                      label="Empleado"
                    >
                      <MenuItem value="">Todos</MenuItem>
                      {empleados.map((emp) => (
                        <MenuItem key={emp.id} value={emp.id}>
                          {emp.nombre}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    variant="contained"
                    startIcon={<FilterListIcon />}
                    onClick={handleFiltrar}
                    fullWidth
                  >
                    Filtrar
                  </Button>
                </Grid>
              </Grid>
            </Paper>

            {/* Botones de acción */}
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => {
                  resetForm();
                  setOpenDialog(true);
                }}
              >
                Nueva Nómina
              </Button>
              <Button
                variant="outlined"
                startIcon={<ExcelIcon />}
                onClick={handleExportarExcel}
              >
                Exportar Excel
              </Button>
            </Box>

            {/* Tabla de nóminas */}
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Empleado</TableCell>
                    <TableCell>Período</TableCell>
                    <TableCell>Días Trabajados</TableCell>
                    <TableCell>Sueldo Base</TableCell>
                    <TableCell>Total</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : nominas.map((nomina) => (
                    <TableRow key={nomina.id}>
                      <TableCell>{nomina.empleado}</TableCell>
                      <TableCell>{nomina.periodo}</TableCell>
                      <TableCell>{nomina.dias_trabajados}</TableCell>
                      <TableCell>${nomina.sueldo_base.toLocaleString()}</TableCell>
                      <TableCell>${nomina.total.toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip
                          label={nomina.estado}
                          color={getEstadoColor(nomina.estado)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Ver detalle">
                          <IconButton onClick={() => handleVerDetalle(nomina)}>
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Editar">
                          <IconButton onClick={() => handleEditar(nomina)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Eliminar">
                          <IconButton onClick={() => handleEliminar(nomina.id)}>
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                        {nomina.estado === 'Pendiente' && (
                          <Tooltip title="Marcar como pagada">
                            <IconButton onClick={() => handleMarcarComoPagada(nomina.id)}>
                              <PaymentIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Exportar PDF">
                          <IconButton onClick={() => handleExportarPDF(nomina)}>
                            <PdfIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}

        {/* Diálogo de detalle */}
        <Dialog
          open={openDetalleDialog}
          onClose={() => setOpenDetalleDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Detalle de Nómina</DialogTitle>
          <DialogContent>
            {nominaSeleccionada && (
              <Box sx={{ p: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="h6">Información General</Typography>
                    <Divider sx={{ my: 1 }} />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Empleado</Typography>
                    <Typography>{nominaSeleccionada.empleado}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Período</Typography>
                    <Typography>{nominaSeleccionada.periodo}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="h6" sx={{ mt: 2 }}>Desglose</Typography>
                    <Divider sx={{ my: 1 }} />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Días Trabajados</Typography>
                    <Typography>{nominaSeleccionada.dias_trabajados}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Sueldo Base</Typography>
                    <Typography>${nominaSeleccionada.sueldo_base.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Horas Extras</Typography>
                    <Typography>{nominaSeleccionada.horas_extras}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Bonificaciones</Typography>
                    <Typography>${nominaSeleccionada.bonificaciones.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Deducciones</Typography>
                    <Typography>${nominaSeleccionada.deducciones.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Total</Typography>
                    <Typography variant="h6" color="primary">
                      ${nominaSeleccionada.total.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="h6" sx={{ mt: 2 }}>Estado</Typography>
                    <Divider sx={{ my: 1 }} />
                    <Chip
                      label={nominaSeleccionada.estado}
                      color={getEstadoColor(nominaSeleccionada.estado)}
                    />
                  </Grid>
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDetalleDialog(false)}>Cerrar</Button>
            <Button
              variant="contained"
              startIcon={<PdfIcon />}
              onClick={() => nominaSeleccionada && handleExportarPDF(nominaSeleccionada)}
            >
              Exportar PDF
            </Button>
          </DialogActions>
        </Dialog>

        {/* Diálogo de crear/editar nómina */}
        <Dialog
          open={openDialog}
          onClose={() => setOpenDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {editMode ? 'Editar Nómina' : 'Nueva Nómina'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth error={!!errors.empleado_id}>
                    <InputLabel>Empleado</InputLabel>
                    <Select
                      value={formData.empleado_id.toString()}
                      onChange={handleEmpleadoChange}
                      label="Empleado"
                    >
                      {empleados.map((emp) => (
                        <MenuItem key={emp.id} value={emp.id}>
                          {emp.nombre}
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.empleado_id && (
                      <FormHelperText>{errors.empleado_id}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Período"
                    name="periodo"
                    value={formData.periodo}
                    onChange={handleTextChange}
                    placeholder="YYYY-MM"
                    error={!!errors.periodo}
                    helperText={errors.periodo}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Días Trabajados"
                    name="dias_trabajados"
                    type="number"
                    value={formData.dias_trabajados}
                    onChange={handleTextChange}
                    error={!!errors.dias_trabajados}
                    helperText={errors.dias_trabajados}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Sueldo Base"
                    name="sueldo_base"
                    type="number"
                    value={formData.sueldo_base}
                    onChange={handleTextChange}
                    error={!!errors.sueldo_base}
                    helperText={errors.sueldo_base}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Horas Extras"
                    name="horas_extras"
                    type="number"
                    value={formData.horas_extras}
                    onChange={handleTextChange}
                    error={!!errors.horas_extras}
                    helperText={errors.horas_extras}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Bonificaciones"
                    name="bonificaciones"
                    type="number"
                    value={formData.bonificaciones}
                    onChange={handleTextChange}
                    error={!!errors.bonificaciones}
                    helperText={errors.bonificaciones}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Deducciones"
                    name="deducciones"
                    type="number"
                    value={formData.deducciones}
                    onChange={handleTextChange}
                    error={!!errors.deducciones}
                    helperText={errors.deducciones}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="h6">
                    Total: ${calcularTotal().toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
            >
              {editMode ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default Nomina;