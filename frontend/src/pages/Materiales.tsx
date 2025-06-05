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
  TablePagination,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  FormHelperText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Inventory as InventoryIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { materialesService, Material, CategoriaMaterial, Proveedor } from '../services/materiales';
import { AxiosError } from 'axios';

// Definición de tipos
type UnidadMedida = {
  value: string;
  label: string;
};

// Tipo para el formulario
type MaterialFormData = {
  codigo: string;
  nombre: string;
  categoria: number | null;
  cantidad: number;
  stock_minimo: number;
  unidad_medida: Material['unidad_medida'];
  precio_unitario: number;
  ubicacion: string;
  proveedor: number | null;
  descripcion: string;
};

const StatusChip = ({ status }: { status: Material['estado_stock'] }) => {
  const config = {
    'Disponible': { color: 'success' as const, icon: <CheckCircleIcon /> },
    'Bajo': { color: 'warning' as const, icon: <WarningIcon /> },
    'Crítico': { color: 'error' as const, icon: <WarningIcon /> },
    'Agotado': { color: 'error' as const, icon: <WarningIcon /> },
  }[status || 'Disponible'];

  return (
    <Chip
      icon={config.icon}
      label={status || 'Desconocido'}
      color={config.color}
      size="small"
    />
  );
};

const estadosStock: Material['estado_stock'][] = ['Disponible', 'Bajo', 'Crítico', 'Agotado'];

const unidadesMedida: UnidadMedida[] = [
  { value: 'un', label: 'Unidad' },
  { value: 'kg', label: 'Kilogramos' },
  { value: 'g', label: 'Gramos' },
  { value: 'l', label: 'Litros' },
  { value: 'ml', label: 'Mililitros' },
  { value: 'm', label: 'Metros' },
  { value: 'cm', label: 'Centímetros' },
  { value: 'm2', label: 'Metros cuadrados' },
  { value: 'm3', label: 'Metros cúbicos' },
  { value: 'pkg', label: 'Paquetes' },
];

const Materiales = () => {
  // Estados principales
  const [materiales, setMateriales] = useState<Material[]>([]);
  const [categorias, setCategorias] = useState<CategoriaMaterial[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingCategorias, setLoadingCategorias] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  
  // Estados para el diálogo de formulario
  const [openDialog, setOpenDialog] = useState(false);
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null);
  const [formData, setFormData] = useState<MaterialFormData>({
    codigo: '',
    nombre: '',
    categoria: null,
    cantidad: 0,
    stock_minimo: 0,
    unidad_medida: 'un',
    precio_unitario: 0,
    ubicacion: '',
    proveedor: null,
    descripcion: ''
  });
  const [formErrors, setFormErrors] = useState({
    codigo: false,
    nombre: false,
    categoria: false,
  });

  // Estados para el diálogo de categoría
  const [openCategoriaDialog, setOpenCategoriaDialog] = useState(false);
  const [categoriaFormData, setCategoriaFormData] = useState<Omit<CategoriaMaterial, 'id'>>({
    codigo: '',
    nombre: '',
    descripcion: '',
    color: '#000000',
    orden: 0,
    activa: true
  });

  // Cargar datos iniciales
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        
        // Cargar materiales y categorías en paralelo
        const [materialesData, categoriasData] = await Promise.all([
          materialesService.getAll(),
          materialesService.getCategorias()
        ]);
        
        setMateriales(materialesData);
        setCategorias(categoriasData);
      } catch (err) {
        console.error('Error al cargar datos:', err);
        setError(err instanceof Error ? err.message : 'Error al cargar los datos');
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // Manejar apertura del diálogo
  const handleOpenDialog = (material?: Material) => {
    if (material) {
      setEditingMaterial(material);
      setFormData({
        codigo: material.codigo,
        nombre: material.nombre,
        categoria: material.categoria,
        cantidad: material.cantidad,
        stock_minimo: material.stock_minimo,
        unidad_medida: material.unidad_medida,
        precio_unitario: material.precio_unitario,
        ubicacion: material.ubicacion || '',
        proveedor: material.proveedor,
        descripcion: material.descripcion || ''
      });
    } else {
      setEditingMaterial(null);
      setFormData({
        codigo: '',
        nombre: '',
        categoria: null,
        cantidad: 0,
        stock_minimo: 0,
        unidad_medida: 'un',
        precio_unitario: 0,
        ubicacion: '',
        proveedor: null,
        descripcion: ''
      });
    }
    setFormErrors({
      codigo: false,
      nombre: false,
      categoria: false,
    });
    setOpenDialog(true);
  };

  // Manejar cierre del diálogo
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingMaterial(null);
    setFormErrors({
      codigo: false,
      nombre: false,
      categoria: false,
    });
  };

  // Validar formulario
  const validateForm = () => {
    const errors = {
      codigo: !formData.codigo.trim(),
      nombre: !formData.nombre.trim(),
      categoria: formData.categoria === null,
    };

    // Validar que el código no esté vacío y tenga un formato válido
    if (!formData.codigo.trim()) {
      errors.codigo = true;
      setError('El código es requerido');
      return false;
    } else if (!/^[A-Za-z0-9-]+$/.test(formData.codigo.trim())) {
      errors.codigo = true;
      setError('El código solo puede contener letras, números y guiones');
      return false;
    }

    // Validar que la cantidad y stock mínimo sean números positivos
    if (formData.cantidad < 0) {
      setError('La cantidad no puede ser negativa');
      return false;
    }

    if (formData.stock_minimo < 0) {
      setError('El stock mínimo no puede ser negativo');
      return false;
    }

    // Validar que el precio unitario sea positivo
    if (formData.precio_unitario < 0) {
      setError('El precio unitario no puede ser negativo');
      return false;
    }

    setFormErrors(errors);
    return !Object.values(errors).some(Boolean);
  };

  // Manejar envío del formulario
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Asegurarnos de que la categoría sea un número
      const categoriaId = formData.categoria ? Number(formData.categoria) : null;
      
      const dataToSubmit = {
        codigo: formData.codigo,
        nombre: formData.nombre,
        categoria: categoriaId,
        cantidad: Number(formData.cantidad),
        stock_minimo: Number(formData.stock_minimo),
        unidad_medida: formData.unidad_medida,
        precio_unitario: Number(formData.precio_unitario),
        ubicacion: formData.ubicacion,
        proveedor: formData.proveedor ? Number(formData.proveedor) : null,
        descripcion: formData.descripcion
      };

      console.log('Datos a enviar:', dataToSubmit); // Para depuración
      
      if (editingMaterial) {
        await materialesService.update(editingMaterial.id, dataToSubmit);
      } else {
        await materialesService.create(dataToSubmit);
      }

      const data = await materialesService.getAll();
      setMateriales(data);
      
      handleCloseDialog();
    } catch (err) {
      console.error('Error al guardar material:', err);
      if (err instanceof Error) {
        if (err.message.includes('Ya existe Material con este codigo')) {
          setError('Ya existe un material con este código. Por favor, use un código diferente.');
        } else {
          setError(err.message);
        }
      } else {
        setError('Error al guardar el material');
      }
    } finally {
      setLoading(false);
    }
  };

  // Manejar eliminación de material
  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Está seguro de que desea eliminar este material?')) {
      return;
    }

    try {
      setLoading(true);
      await materialesService.delete(id);
      setMateriales(prev => prev.filter(m => m.id !== id));
      setError(null);
    } catch (err) {
      console.error('Error al eliminar material:', err);
      setError(err instanceof Error ? err.message : 'Error al eliminar el material');
    } finally {
      setLoading(false);
    }
  };

  // Calcular resumen
  const totalMateriales = materiales.length;
  const stockBajo = materiales.filter(m => m.estado_stock === 'Bajo').length;
  const stockCritico = materiales.filter(m => m.estado_stock === 'Crítico' || m.estado_stock === 'Agotado').length;

  // Manejar apertura del diálogo de categoría
  const handleOpenCategoriaDialog = () => {
    setCategoriaFormData({
      codigo: '',
      nombre: '',
      descripcion: '',
      color: '#000000',
      orden: 0,
      activa: true
    });
    setOpenCategoriaDialog(true);
  };

  // Manejar cierre del diálogo de categoría
  const handleCloseCategoriaDialog = () => {
    setOpenCategoriaDialog(false);
  };

  // Manejar envío del formulario de categoría
  const handleSubmitCategoria = async () => {
    try {
      setLoadingCategorias(true);
      await materialesService.createCategoria(categoriaFormData);
      const categoriasData = await materialesService.getCategorias();
      setCategorias(categoriasData);
      handleCloseCategoriaDialog();
    } catch (err) {
      console.error('Error al crear categoría:', err);
      setError(err instanceof Error ? err.message : 'Error al crear la categoría');
    } finally {
      setLoadingCategorias(false);
    }
  };

  if (loading && !openDialog) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gestión de Materiales
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          aria-label="Agregar nuevo material"
          disabled={loading}
        >
          Nuevo Material
        </Button>
      </Box>

      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
          action={
            <IconButton
              aria-label="cerrar"
              color="inherit"
              size="small"
              onClick={() => setError(null)}
            >
              <CancelIcon fontSize="inherit" />
            </IconButton>
          }
        >
          {error}
        </Alert>
      )}

      {loading && !openDialog ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper sx={{ width: '100%', mb: 2 }}>
          <TableContainer>
            <Table sx={{ minWidth: 750 }} aria-labelledby="tabla-materiales">
              <TableHead>
                <TableRow>
                  <TableCell>Código</TableCell>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Categoría</TableCell>
                  <TableCell>Cantidad</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell align="right">Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {materiales.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No hay materiales registrados
                    </TableCell>
                  </TableRow>
                ) : (
                  materiales
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((material) => (
                      <TableRow key={material.id}>
                        <TableCell>{material.codigo}</TableCell>
                        <TableCell>{material.nombre}</TableCell>
                        <TableCell>{material.categoria_nombre}</TableCell>
                        <TableCell>{material.cantidad} {material.unidad_medida}</TableCell>
                        <TableCell>
                          <StatusChip status={material.estado_stock} />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton
                            onClick={() => handleOpenDialog(material)}
                            aria-label="Editar material"
                            size="small"
                            disabled={loading}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            onClick={() => handleDelete(material.id)}
                            aria-label="Eliminar material"
                            size="small"
                            disabled={loading}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={materiales.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            onRowsPerPageChange={(event) => {
              setRowsPerPage(parseInt(event.target.value, 10));
              setPage(0);
            }}
            labelRowsPerPage="Filas por página"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
          />
        </Paper>
      )}

      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        aria-labelledby="material-dialog-title"
        disableEnforceFocus
        keepMounted
        maxWidth="md"
        fullWidth
        slotProps={{
          backdrop: {
            sx: {
              backgroundColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }}
      >
        <DialogTitle id="material-dialog-title">
          {editingMaterial ? 'Editar Material' : 'Nuevo Material'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Código"
                  value={formData.codigo}
                  onChange={(e) => setFormData({...formData, codigo: e.target.value})}
                  error={formErrors.codigo}
                  helperText={formErrors.codigo ? 'El código es requerido y solo puede contener letras, números y guiones' : ''}
                  margin="normal"
                  disabled={loading}
                  required
                  inputProps={{
                    'aria-label': 'Código del material'
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  error={formErrors.nombre}
                  helperText={formErrors.nombre ? 'El nombre es requerido' : ''}
                  margin="normal"
                  required
                  disabled={loading}
                  inputProps={{
                    'aria-label': 'Nombre del material'
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth margin="normal" error={formErrors.categoria}>
                  <InputLabel>Categoría</InputLabel>
                  <Select
                    value={formData.categoria || ''}
                    label="Categoría"
                    onChange={(e) => {
                      const value = e.target.value;
                      setFormData({ 
                        ...formData, 
                        categoria: value === '' ? null : Number(value)
                      });
                    }}
                    disabled={loading}
                    inputProps={{
                      'aria-label': 'Categoría del material'
                    }}
                  >
                    <MenuItem value="">
                      <em>Seleccione una categoría</em>
                    </MenuItem>
                    {categorias.map((categoria) => (
                      <MenuItem key={categoria.id} value={categoria.id}>
                        {categoria.nombre}
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.categoria && (
                    <FormHelperText>La categoría es requerida</FormHelperText>
                  )}
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Unidad de Medida</InputLabel>
                  <Select
                    value={formData.unidad_medida}
                    onChange={(e) => setFormData({
                      ...formData, 
                      unidad_medida: e.target.value as Material['unidad_medida']
                    })}
                    label="Unidad de Medida"
                    disabled={loading}
                    inputProps={{
                      'aria-label': 'Unidad de medida del material'
                    }}
                  >
                    {unidadesMedida.map((unidad) => (
                      <MenuItem key={unidad.value} value={unidad.value}>
                        {unidad.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Cantidad"
                  type="number"
                  value={formData.cantidad}
                  onChange={(e) => setFormData({
                    ...formData, 
                    cantidad: Number(e.target.value)
                  })}
                  margin="normal"
                  inputProps={{ 
                    min: 0,
                    'aria-label': 'Cantidad del material'
                  }}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Stock Mínimo"
                  type="number"
                  value={formData.stock_minimo}
                  onChange={(e) => setFormData({
                    ...formData, 
                    stock_minimo: Number(e.target.value)
                  })}
                  margin="normal"
                  inputProps={{ 
                    min: 0,
                    'aria-label': 'Stock mínimo del material'
                  }}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Precio Unitario"
                  type="number"
                  value={formData.precio_unitario}
                  onChange={(e) => setFormData({
                    ...formData, 
                    precio_unitario: Number(e.target.value)
                  })}
                  margin="normal"
                  inputProps={{ 
                    min: 0,
                    'aria-label': 'Precio unitario del material'
                  }}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Ubicación"
                  value={formData.ubicacion}
                  onChange={(e) => setFormData({
                    ...formData, 
                    ubicacion: e.target.value
                  })}
                  margin="normal"
                  disabled={loading}
                  inputProps={{
                    'aria-label': 'Ubicación del material'
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Descripción"
                  value={formData.descripcion}
                  onChange={(e) => setFormData({
                    ...formData, 
                    descripcion: e.target.value
                  })}
                  margin="normal"
                  multiline
                  rows={3}
                  disabled={loading}
                  inputProps={{
                    'aria-label': 'Descripción del material'
                  }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={loading}>
            Cancelar
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {loading ? 'Guardando...' : 'Guardar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo de categoría */}
      <Dialog open={openCategoriaDialog} onClose={handleCloseCategoriaDialog}>
        <DialogTitle>Nueva Categoría</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Código"
                value={categoriaFormData.codigo}
                onChange={(e) => setCategoriaFormData({ ...categoriaFormData, codigo: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nombre"
                value={categoriaFormData.nombre}
                onChange={(e) => setCategoriaFormData({ ...categoriaFormData, nombre: e.target.value })}
                margin="normal"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descripción"
                value={categoriaFormData.descripcion}
                onChange={(e) => setCategoriaFormData({ ...categoriaFormData, descripcion: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Color"
                type="color"
                value={categoriaFormData.color}
                onChange={(e) => setCategoriaFormData({ ...categoriaFormData, color: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Orden"
                type="number"
                value={categoriaFormData.orden}
                onChange={(e) => setCategoriaFormData({ ...categoriaFormData, orden: parseInt(e.target.value) })}
                margin="normal"
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Estado</InputLabel>
                <Select
                  value={categoriaFormData.activa ? 'true' : 'false'}
                  onChange={(e) => setCategoriaFormData({ 
                    ...categoriaFormData, 
                    activa: e.target.value === 'true' 
                  })}
                  label="Estado"
                >
                  <MenuItem value="true">Activa</MenuItem>
                  <MenuItem value="false">Inactiva</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCategoriaDialog}>Cancelar</Button>
          <Button onClick={handleSubmitCategoria} variant="contained" color="primary">
            Guardar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Materiales;