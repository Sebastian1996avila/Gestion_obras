# Sistema de Gestión de Obras

Sistema integral para la gestión de obras de construcción, desarrollado con Django y React.

## Características

- Gestión de proyectos y obras
- Control de materiales y inventario
- Gestión de nómina y personal
- Control de asistencia
- Gestión de usuarios y permisos
- API REST para integración con otros sistemas

## Requisitos

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Sebastian1996avila/gestion-obras.git
cd gestion-obras
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias de Python:
```bash
pip install -r requirements.txt
```

4. Instalar dependencias de Node.js:
```bash
cd frontend
npm install
```

5. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

6. Aplicar migraciones:
```bash
python manage.py migrate
```

7. Crear superusuario:
```bash
python manage.py createsuperuser
```

8. Iniciar servidor de desarrollo:
```bash
# Backend
python manage.py runserver

# Frontend (en otra terminal)
cd frontend
npm run dev
```

## Estructura del Proyecto

```
gestion-obras/
├── backend/           # API Django
├── frontend/          # Aplicación React
├── asistencia/        # Módulo de asistencia
├── materiales/        # Módulo de materiales
├── nomina/           # Módulo de nómina
├── obras/            # Módulo de obras
├── proyectos/        # Módulo de proyectos
└── usuarios/         # Módulo de usuarios
```

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Sebastián Ávila - sebastian1996avila@gmail.com

Link del proyecto: [https://github.com/Sebastian1996avila/gestion-obras](https://github.com/Sebastian1996avila/gestion-obras)

## Despliegue

### Despliegue Local

1. Asegúrate de que todas las dependencias estén instaladas
2. Configura las variables de entorno
3. Inicia el servidor de base de datos PostgreSQL
4. Ejecuta las migraciones
5. Inicia el servidor backend
6. Inicia el servidor frontend

### Despliegue en Producción

1. Configurar el servidor web (Nginx/Apache)
2. Configurar Gunicorn como servidor WSGI
3. Configurar SSL/TLS
4. Actualizar las variables de entorno para producción
5. Configurar el servicio de base de datos
6. Configurar el servicio de archivos estáticos

## Soporte

Para reportar problemas o solicitar ayuda, por favor crear un issue en el repositorio del proyecto.
