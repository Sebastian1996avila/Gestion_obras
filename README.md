# Sistema de Gestión de Obras

Este sistema permite la gestión integral de obras, incluyendo control de asistencia, nómina, materiales y proyectos.

## Requisitos Previos

- Python 3.8 o superior
- Node.js 14.x o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)
- npm (gestor de paquetes de Node.js)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd gestion_obras
```

### 2. Configuración del Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalación de Dependencias

```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js
npm install
```

### 4. Configuración de Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DEBUG=True
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Configuración de la Base de Datos

1. Crear una base de datos PostgreSQL:
```sql
CREATE DATABASE nombre_db;
```

2. Aplicar las migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Crear un superusuario:
```bash
python manage.py createsuperuser
```

### 6. Ejecución del Proyecto

#### Backend (Django)
```bash
# En modo desarrollo
python manage.py runserver

# En modo producción
gunicorn gestion_obras.wsgi:application
```

#### Frontend
```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

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

## Estructura del Proyecto

```
gestion_obras/
├── backend/           # API REST
├── frontend/          # Aplicación React
├── database/          # Scripts de base de datos
├── templates/         # Plantillas HTML
├── staticfiles/       # Archivos estáticos
├── media/            # Archivos multimedia
└── manage.py         # Script de administración de Django
```

## Soporte

Para reportar problemas o solicitar ayuda, por favor crear un issue en el repositorio del proyecto.

## Licencia
