import axios from 'axios';
import { store } from '../store';
import { logout } from '../store/slices/authSlice';

// Configuración base de la API
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true, // Necesario para cookies en autenticación por sesión
});

/**
 * Interceptor para manejar autenticación
 */
api.interceptors.request.use(
  (config) => {
    console.log('Request:', config.method?.toUpperCase(), config.url);
    // Agregar token de autenticación si existe (JWT)
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Interceptor de respuestas
 */
api.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.config.url);
    return response;
  },
  async (error) => {
    console.error('Response Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    const originalRequest = error.config;
    const isLoginPage = window.location.pathname === '/login';
    
    if (error.response) {
      switch (error.response.status) {
        case 401: // No autorizado
          if (!isLoginPage && !originalRequest._retry) {
            // Intentar refrescar el token
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              try {
                originalRequest._retry = true;
                const refreshResponse = await api.post('/api/auth/refresh/', {
                  refresh: refreshToken
                });
                
                localStorage.setItem('token', refreshResponse.data.access);
                originalRequest.headers['Authorization'] = `Bearer ${refreshResponse.data.access}`;
                return api(originalRequest);
              } catch (refreshError) {
                // Solo cerrar sesión si no estamos en la página de login
                if (!isLoginPage) {
                  logoutUser();
                }
              }
            } else if (!isLoginPage) {
              // Solo cerrar sesión si no estamos en la página de login
              logoutUser();
            }
          }
          break;
        case 405: // Method Not Allowed
          // Si es una petición a login, redirigir al login
          if (originalRequest.url?.includes('/api/auth/login/')) {
            window.location.href = '/login';
          }
          break;
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Función para obtener el valor de una cookie
 */
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

/**
 * Función mejorada para cerrar sesión
 */
function logoutUser(): void {
  // Limpiar almacenamiento local
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  
  // Limpiar estado de Redux
  store.dispatch(logout());
  
  // Redirigir al login
  window.location.href = '/login';
}

export default api;