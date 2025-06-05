import api from './api';

export type EstadoProyecto = 'PLAN' | 'EJE' | 'SUS' | 'COM' | 'CAN';

export interface Proyecto {
  id: number;
  nombre: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_fin: string | null;
  estado: EstadoProyecto;
  presupuesto: number;
  activo: boolean;
  foto?: File | null;
  foto_url?: string;
  responsable?: number;
  responsable_info?: {
    id: number;
    nombre: string;
    email: string;
  };
  asignados?: number[];
}

const estadoMap: Record<EstadoProyecto, string> = {
  PLAN: 'Planificado',
  EJE: 'En Ejecución',
  SUS: 'Suspendido',
  COM: 'Completado',
  CAN: 'Cancelado'
};

export const proyectosService = {
  getAll: async (): Promise<Proyecto[]> => {
    try {
      const response = await api.get<Proyecto[]>('/api/proyectos/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener proyectos:', error);
      throw new Error('No se pudieron obtener los proyectos. Por favor, intente nuevamente.');
    }
  },

  getById: async (id: number): Promise<Proyecto> => {
    try {
      const response = await api.get<Proyecto>(`/api/proyectos/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener proyecto ${id}:`, error);
      throw new Error('No se pudo obtener el proyecto. Por favor, intente nuevamente.');
    }
  },

  create: async (proyecto: Omit<Proyecto, 'id'>): Promise<Proyecto> => {
    try {
      const formData = new FormData();
      
      // Validaciones básicas
      if (!proyecto.nombre?.trim()) {
        throw new Error('El nombre del proyecto es requerido');
      }
      if (!proyecto.fecha_inicio) {
        throw new Error('La fecha de inicio es requerida');
      }
      
      // Agregar campos básicos
      formData.append('nombre', proyecto.nombre.trim());
      formData.append('descripcion', proyecto.descripcion || '');
      formData.append('fecha_inicio', proyecto.fecha_inicio);
      if (proyecto.fecha_fin) {
        formData.append('fecha_fin', proyecto.fecha_fin);
      }
      formData.append('estado', proyecto.estado || 'PLAN');
      formData.append('presupuesto', proyecto.presupuesto.toString());
      formData.append('activo', proyecto.activo.toString());
      
      // Agregar foto si existe
      if (proyecto.foto) {
        formData.append('foto', proyecto.foto);
      }
      
      // Agregar responsable si existe
      if (proyecto.responsable) {
        formData.append('responsable', proyecto.responsable.toString());
      }
      
      // Agregar asignados si existen
      if (proyecto.asignados && proyecto.asignados.length > 0) {
        proyecto.asignados.forEach(id => {
          formData.append('asignados', id.toString());
        });
      }

      const response = await api.post<Proyecto>('/api/proyectos/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error al crear proyecto:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('No se pudo crear el proyecto. Por favor, intente nuevamente.');
    }
  },

  update: async (id: number, proyecto: Partial<Proyecto>): Promise<Proyecto> => {
    try {
      const formData = new FormData();
      
      // Validaciones básicas
      if (proyecto.nombre && !proyecto.nombre.trim()) {
        throw new Error('El nombre del proyecto no puede estar vacío');
      }
      
      // Agregar campos básicos
      if (proyecto.nombre) formData.append('nombre', proyecto.nombre.trim());
      if (proyecto.descripcion) formData.append('descripcion', proyecto.descripcion);
      if (proyecto.fecha_inicio) formData.append('fecha_inicio', proyecto.fecha_inicio);
      if (proyecto.fecha_fin) formData.append('fecha_fin', proyecto.fecha_fin);
      if (proyecto.estado) formData.append('estado', proyecto.estado);
      if (proyecto.presupuesto !== undefined) formData.append('presupuesto', proyecto.presupuesto.toString());
      if (proyecto.activo !== undefined) formData.append('activo', proyecto.activo.toString());
      
      // Agregar foto si existe
      if (proyecto.foto) {
        formData.append('foto', proyecto.foto);
      }
      
      // Agregar responsable si existe
      if (proyecto.responsable) {
        formData.append('responsable', proyecto.responsable.toString());
      }
      
      // Agregar asignados si existen
      if (proyecto.asignados && proyecto.asignados.length > 0) {
        proyecto.asignados.forEach(id => {
          formData.append('asignados', id.toString());
        });
      }

      const response = await api.patch<Proyecto>(`/api/proyectos/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar proyecto ${id}:`, error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('No se pudo actualizar el proyecto. Por favor, intente nuevamente.');
    }
  },

  delete: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/proyectos/${id}/`);
    } catch (error) {
      console.error(`Error al eliminar proyecto ${id}:`, error);
      throw new Error('No se pudo eliminar el proyecto. Por favor, intente nuevamente.');
    }
  },

  getEstadoDisplay: (estado: EstadoProyecto): string => {
    return estadoMap[estado] || 'Desconocido';
  }
}; 