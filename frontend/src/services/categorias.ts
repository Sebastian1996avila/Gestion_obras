
import api from './api'; // Asume que tienes una instancia configurada de axios

export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

export const categoriasService = {
  async getAll(): Promise<Categoria[]> {
    try {
      const response = await api.get('/categorias');
      return response.data;
    } catch (error) {
      console.error('Error al obtener categorías:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<Categoria> {
    try {
      const response = await api.get(`/categorias/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener categoría con ID ${id}:`, error);
      throw error;
    }
  },

  async create(categoria: Omit<Categoria, 'id'>): Promise<Categoria> {
    try {
      const response = await api.post('/categorias', categoria);
      return response.data;
    } catch (error) {
      console.error('Error al crear categoría:', error);
      throw error;
    }
  },

  async update(id: number, categoria: Partial<Categoria>): Promise<Categoria> {
    try {
      const response = await api.put(`/categorias/${id}`, categoria);
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar categoría con ID ${id}:`, error);
      throw error;
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await api.delete(`/categorias/${id}`);
    } catch (error) {
      console.error(`Error al eliminar categoría con ID ${id}:`, error);
      throw error;
    }
  }
};