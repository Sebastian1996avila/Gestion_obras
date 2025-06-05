import api from './api';

/**
 * Tipos e interfaces mejorados
 */
export type NominaEstado = 'Pendiente' | 'Pagado' | 'Cancelado';

export interface NominaResponse {
  id: number;
  empleado: string;
  empleado_id: number;
  periodo: string;
  dias_trabajados: number;
  sueldo_base: number;
  horas_extras: number;
  bonificaciones: number;
  deducciones: number;
  total: number;
  estado: NominaEstado;
  creado_en: string;
  actualizado_en: string;
}

export interface NominaCreatePayload {
  empleado_id: number;
  periodo: string; // Formato: 'YYYY-MM'
  dias_trabajados: number;
  sueldo_base: number;
  horas_extras?: number;
  bonificaciones?: number;
  deducciones?: number;
}

export interface NominaUpdatePayload extends Partial<NominaCreatePayload> {
  estado?: NominaEstado;
}

/**
 * Servicio de Nómina mejorado
 */
export const nominaService = {
  /**
   * Obtener todas las nóminas
   */
  getAll: async (): Promise<NominaResponse[]> => {
    try {
      const response = await api.get<NominaResponse[]>('/api/nomina/');
      return response.data;
    } catch (error: any) {
      console.error('Error al obtener nóminas:', error);
      if (error.response) {
        // El servidor respondió con un código de estado fuera del rango 2xx
        throw new Error(error.response.data?.message || 'Error al obtener las nóminas');
      } else if (error.request) {
        // La petición fue hecha pero no se recibió respuesta
        throw new Error('No se pudo conectar con el servidor. Verifique su conexión a internet.');
      } else {
        // Algo sucedió al configurar la petición
        throw new Error('Error al procesar la solicitud');
      }
    }
  },

  /**
   * Obtener nómina por ID
   */
  getById: async (id: number): Promise<NominaResponse> => {
    if (!id || isNaN(id)) {
      throw new Error('ID de nómina inválido');
    }

    try {
      const response = await api.get<NominaResponse>(`/api/nomina/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error(`Error al obtener nómina ${id}:`, error);
      if (error.response?.status === 404) {
        throw new Error('Nómina no encontrada');
      }
      throw new Error('Error al obtener la nómina');
    }
  },

  /**
   * Crear nueva nómina
   */
  create: async (payload: NominaCreatePayload): Promise<NominaResponse> => {
    try {
      // Validaciones frontend
      if (!payload.empleado_id || isNaN(payload.empleado_id)) {
        throw new Error('ID de empleado inválido');
      }

      if (!payload.periodo.match(/^\d{4}-\d{2}$/)) {
        throw new Error('Formato de período inválido. Use YYYY-MM');
      }

      if (payload.dias_trabajados <= 0 || payload.dias_trabajados > 31) {
        throw new Error('Días trabajados deben estar entre 1 y 31');
      }

      if (payload.sueldo_base <= 0) {
        throw new Error('Sueldo base debe ser mayor a 0');
      }

      // Asegurarse de que los campos opcionales tengan valores por defecto
      const completePayload = {
        empleado_id: payload.empleado_id,
        periodo: payload.periodo,
        dias_trabajados: payload.dias_trabajados,
        sueldo_base: payload.sueldo_base,
        horas_extras: payload.horas_extras || 0,
        bonificaciones: payload.bonificaciones || 0,
        deducciones: payload.deducciones || 0
      };

      console.log('Enviando payload:', completePayload); // Para debugging

      const response = await api.post<NominaResponse>('/api/nomina/', completePayload);
      console.log('Respuesta del servidor:', response.data); // Para debugging
      return response.data;
    } catch (error: any) {
      console.error('Error al crear nómina:', error);
      if (error.response?.status === 400) {
        const backendErrors = error.response.data;
        let errorMessage = 'Errores de validación:';
        
        if (typeof backendErrors === 'object') {
          for (const [field, errors] of Object.entries(backendErrors)) {
            errorMessage += `\n${field}: ${(errors as string[]).join(', ')}`;
          }
        } else {
          errorMessage += `\n${backendErrors}`;
        }
        
        throw new Error(errorMessage);
      }
      
      if (error.response?.status === 403) {
        throw new Error('No tiene permisos para crear nóminas');
      }
      
      throw new Error('Error al crear la nómina');
    }
  },

  /**
   * Actualizar nómina
   */
  update: async (id: number, payload: NominaUpdatePayload): Promise<NominaResponse> => {
    if (!id || isNaN(id)) {
      throw new Error('ID de nómina inválido');
    }

    try {
      const response = await api.patch<NominaResponse>(`/api/nomina/${id}/`, payload);
      return response.data;
    } catch (error: any) {
      console.error(`Error al actualizar nómina ${id}:`, error);
      if (error.response?.status === 400) {
        throw new Error('Datos inválidos para actualizar la nómina');
      }
      if (error.response?.status === 403) {
        throw new Error('No tiene permisos para actualizar esta nómina');
      }
      if (error.response?.status === 404) {
        throw new Error('Nómina no encontrada');
      }
      throw new Error('Error al actualizar la nómina');
    }
  },

  /**
   * Eliminar nómina
   */
  delete: async (id: number): Promise<void> => {
    if (!id || isNaN(id)) {
      throw new Error('ID de nómina inválido');
    }

    try {
      await api.delete(`/api/nomina/${id}/`);
    } catch (error: any) {
      console.error(`Error al eliminar nómina ${id}:`, error);
      if (error.response?.status === 403) {
        throw new Error('No tiene permisos para eliminar esta nómina');
      }
      if (error.response?.status === 404) {
        throw new Error('Nómina no encontrada');
      }
      throw new Error('Error al eliminar la nómina');
    }
  },

  /**
   * Obtener nóminas por período
   */
  getByPeriodo: async (periodo: string): Promise<NominaResponse[]> => {
    if (!periodo.match(/^\d{4}-\d{2}$/)) {
      throw new Error('Formato de período inválido. Use YYYY-MM');
    }

    try {
      const response = await api.get<NominaResponse[]>(`/api/nomina/periodo/${periodo}/`);
      return response.data;
    } catch (error: any) {
      console.error(`Error al obtener nóminas del período ${periodo}:`, error);
      if (error.response?.status === 404) {
        return [];
      }
      throw new Error('Error al obtener nóminas del período');
    }
  },

  /**
   * Obtener nóminas por empleado
   */
  getByEmpleado: async (empleadoId: number): Promise<NominaResponse[]> => {
    if (!empleadoId || isNaN(empleadoId)) {
      throw new Error('ID de empleado inválido');
    }

    try {
      const response = await api.get<NominaResponse[]>(`/api/nomina/empleado/${empleadoId}/`);
      return response.data;
    } catch (error: any) {
      console.error(`Error al obtener nóminas del empleado ${empleadoId}:`, error);
      if (error.response?.status === 404) {
        return [];
      }
      throw new Error('Error al obtener nóminas del empleado');
    }
  },

  /**
   * Procesar nómina (cambiar estado a Pagado) con validación
   */
  procesarNomina: async (id: number): Promise<NominaResponse> => {
    if (!id || isNaN(id)) {
      throw new Error('ID de nómina inválido');
    }

    try {
      const response = await api.post<NominaResponse>(`/api/nomina/${id}/procesar/`, {}, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error('No se puede procesar una nómina cancelada');
      }
      if (error.response?.status === 403) {
        throw new Error('No tiene permisos para procesar nóminas');
      }
      if (error.response?.status === 404) {
        throw new Error('Nómina no encontrada');
      }
      
      console.error(`Error al procesar nómina con ID ${id}:`, error);
      throw new Error('No se pudo procesar la nómina.');
    }
  }
};