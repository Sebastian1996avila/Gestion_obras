import api from './api';

export interface Empleado {
  id: number;
  nombre: string;
  email: string;
  rol: 'ADM' | 'SUP' | 'ARQ' | 'TEC';
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export const empleadosService = {
  getAll: async (): Promise<Empleado[]> => {
    try {
      const response = await api.get<Empleado[]>('/api/usuarios/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener empleados:', error);
      throw new Error('No se pudieron obtener los empleados. Por favor, intente nuevamente.');
    }
  },

  getById: async (id: number): Promise<Empleado> => {
    try {
      const response = await api.get<Empleado>(`/api/usuarios/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener empleado ${id}:`, error);
      throw new Error('No se pudo obtener el empleado. Por favor, intente nuevamente.');
    }
  }
}; 