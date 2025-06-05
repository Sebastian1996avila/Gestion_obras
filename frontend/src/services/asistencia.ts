import api from './api';
import { AxiosError } from 'axios';

export interface Asistencia {
  id: number;
  usuario: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    rol: string;
  };
  fecha: string;
  hora: string;
  tipo: 'ENT' | 'SAL';
  ubicacion?: string;
  observaciones?: string;
  estado: 'PENDIENTE' | 'APROBADO' | 'RECHAZADO';
}

export interface AsistenciaCreate {
  tipo: 'ENT' | 'SAL';
  ubicacion?: string;
  observaciones?: string;
  usuario_id?: number;
  fecha?: string;
  hora?: string;
}

export const asistenciaService = {
  getAll: async (): Promise<Asistencia[]> => {
    try {
      const response = await api.get('/api/asistencia/registros/');
      return response.data;
    } catch (error) {
      console.error('Error al obtener asistencias:', error);
      throw error;
    }
  },

  getById: async (id: number) => {
    try {
      const response = await api.get<Asistencia>(`/api/asistencia/registrar/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener asistencia por ID:', error);
      throw error;
    }
  },

  create: async (data: AsistenciaCreate): Promise<Asistencia> => {
    try {
      // Asegurarse de que la fecha y hora estén en el formato correcto
      const now = new Date();
      const dataToSend = {
        ...data,
        fecha: data.fecha || now.toISOString().split('T')[0],
        hora: data.hora || now.toTimeString().split(' ')[0]
      };

      const response = await api.post('/api/asistencia/registrar/', dataToSend, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error al crear asistencia:', error);
      if (error instanceof AxiosError && error.response?.data) {
        throw new Error(JSON.stringify(error.response.data));
      }
      throw error;
    }
  },

  update: async (id: number, data: Partial<Asistencia>): Promise<Asistencia> => {
    try {
      const response = await api.put(`/api/asistencia/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al actualizar asistencia:', error);
      throw error;
    }
  },

  delete: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/asistencia/${id}/`);
    } catch (error) {
      console.error('Error al eliminar asistencia:', error);
      throw error;
    }
  },

  getResumen: async (fechaInicio?: string, fechaFin?: string) => {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get('/api/asistencia/resumen/', { params });
    return response.data;
  },

  getRegistrosAdmin: async (usuarioId?: number, fechaInicio?: string, fechaFin?: string) => {
    const params = new URLSearchParams();
    if (usuarioId) params.append('usuario_id', usuarioId.toString());
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get<Asistencia[]>('/api/asistencia/registros/', { params });
    return response.data;
  }
};