import api from './api';

export interface CategoriaMaterial {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  color: string;
  orden: number;
  activa: boolean;
}

export interface Proveedor {
  id: number;
  nombre: string;
  contacto: string;
  telefono: string;
  email: string;
  direccion: string;
}

export interface Material {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: number | null;
  categoria_nombre?: string;
  cantidad: number;
  unidad_medida: 'kg' | 'g' | 'l' | 'ml' | 'm' | 'cm' | 'm2' | 'm3' | 'un' | 'pkg';
  precio_unitario: number;
  stock_minimo: number;
  estado_stock?: 'Agotado' | 'Crítico' | 'Bajo' | 'Disponible';
  ubicacion: string;
  proveedor: number | null;
  proveedor_nombre?: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

// Función para obtener el token CSRF de las cookies
function getCSRFToken(): string | null {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Función para configurar los headers de la petición
function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const csrfToken = getCSRFToken();
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken;
  }

  return headers;
}

// Función para manejar errores de la API
function handleApiError(error: any, operation: string): never {
  console.error(`Error al ${operation}:`, error);
  
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    if (status === 403) {
      throw new Error('No tienes permisos para realizar esta operación');
    }

    if (status === 400) {
      const errorMessage = typeof data === 'object' ? Object.values(data).flat().join(', ') : data;
      throw new Error(`Error de validación: ${errorMessage}`);
    }

    if (status === 404) {
      throw new Error('El recurso solicitado no fue encontrado');
    }

    throw new Error(`Error del servidor (${status}): ${data.detail || 'Error desconocido'}`);
  }

  if (error.request) {
    throw new Error('No se pudo conectar con el servidor. Por favor, verifica tu conexión');
  }

  throw new Error(`Error al ${operation}: ${error.message}`);
}

export const materialesService = {
  getAll: async (): Promise<Material[]> => {
    try {
      const response = await api.get<Material[]>('/api/materiales/');
      return response.data;
    } catch (error) {
      throw handleApiError(error, 'obtener materiales');
    }
  },

  getById: async (id: number) => {
    try {
      const response = await api.get<Material>(`/api/materiales/${id}/`);
      return response.data;
    } catch (error) {
      throw handleApiError(error, 'obtener material');
    }
  },

  create: async (material: Omit<Material, 'id' | 'fecha_creacion' | 'fecha_actualizacion' | 'estado_stock' | 'categoria_nombre' | 'proveedor_nombre'>) => {
    try {
      // Asegurarnos de que la categoría sea un número
      const materialData = {
        ...material,
        categoria: material.categoria ? Number(material.categoria) : null,
        proveedor: material.proveedor ? Number(material.proveedor) : null
      };
      const response = await api.post<Material>('/api/materiales/', materialData);
      return response.data;
    } catch (error) {
      throw handleApiError(error, 'crear material');
    }
  },

  update: async (id: number, material: Partial<Material>) => {
    try {
      // Asegurarnos de que la categoría sea un número
      const materialData = {
        ...material,
        categoria: material.categoria ? Number(material.categoria) : null,
        proveedor: material.proveedor ? Number(material.proveedor) : null
      };
      const response = await api.put<Material>(`/api/materiales/${id}/`, materialData);
      return response.data;
    } catch (error) {
      throw handleApiError(error, 'actualizar material');
    }
  },

  delete: async (id: number) => {
    try {
      await api.delete(`/api/materiales/${id}/`);
    } catch (error) {
      throw handleApiError(error, 'eliminar material');
    }
  },

  getCategorias: async () => {
    try {
      const response = await api.get<CategoriaMaterial[]>('/api/materiales/categorias/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener categorías:', error);
      return [];
    }
  },

  createCategoria: async (categoria: Omit<CategoriaMaterial, 'id'>) => {
    try {
      const response = await api.post<CategoriaMaterial>('/api/materiales/categorias/', categoria);
      return response.data;
    } catch (error) {
      throw handleApiError(error, 'crear categoría');
    }
  },

  getProveedores: async () => {
    try {
      const response = await api.get<Proveedor[]>('/api/materiales/proveedores/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener proveedores:', error);
      return [];
    }
  },

  createProveedor: async (proveedor: Omit<Proveedor, 'id'>) => {
    try {
      const response = await api.post<Proveedor>('/api/materiales/proveedores/', proveedor);
      return response.data;
    } catch (error) {
      throw handleApiError(error, 'crear proveedor');
    }
  },

  getEstadisticas: async () => {
    try {
      const response = await api.get('/api/materiales/estadisticas/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      throw error;
    }
  },

  getEstadoDisplay: (estado: Material['estado_stock']): string => {
    return estado || 'Desconocido';
  }
}; 