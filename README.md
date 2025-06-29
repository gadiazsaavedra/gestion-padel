# 🏓 Club de Pádel - Sistema de Gestión

Sistema completo de gestión para club de pádel desarrollado en Django.

## 🚀 Características

### 👥 Gestión de Usuarios
- **Administradores**: Control total del sistema
- **Recepcionistas**: Operaciones diarias (POS, reservas)
- **Jugadores**: Perfil personal, reservas, emparejamiento

### 🛒 Sistema POS
- Punto de venta completo
- Gestión de stock e inventario
- Reportes de ventas y márgenes
- Códigos de barras y tickets

### 📅 Reservas
- Sistema de reservas online
- Gestión de canchas y horarios
- Emparejamiento de jugadores

### 📊 Reportes
- Ventas por período
- Productos más vendidos
- Control de márgenes
- Análisis de proveedores

## 🛠️ Tecnologías

- **Backend**: Django 5.2.3
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Base de datos**: SQLite (desarrollo)
- **Autenticación**: Django Auth
- **UI/UX**: Responsive design, menús dinámicos

## 📦 Instalación

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd club-padel

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Configurar roles
python manage.py setup_roles

# Ejecutar servidor
python manage.py runserver
```

## 🐳 Ejecución con Docker

Este proyecto incluye configuración lista para Docker y Docker Compose, permitiendo levantar tanto el backend de Django como el frontend (build de Tailwind CSS) de forma sencilla.

### Requisitos
- **Docker** y **Docker Compose** instalados
- No se requieren variables de entorno obligatorias por defecto, pero puedes usar archivos `.env` si lo necesitas (ver comentarios en `docker-compose.yml`)
- El backend usa **Python 3.11** (imagen `python:3.11-slim`)
- El frontend usa **Node.js 22.13.1** (imagen `node:22.13.1-slim`)

### Puertos expuestos
- **Backend Django**: `8000` (http://localhost:8000)
- **Frontend**: No expone puertos por defecto (el contenedor solo construye los assets de Tailwind CSS)

### Instrucciones rápidas

```bash
# Construir y levantar los servicios
# (desde la raíz del proyecto)
docker compose up --build
```

Esto levantará:
- `python-app`: Servidor Django accesible en http://localhost:8000
- `js-frontend`: Construye los assets de Tailwind CSS (no expone puertos)

### Notas y configuración especial
- Si necesitas variables de entorno, descomenta las líneas `env_file` en el `docker-compose.yml` y agrega tus archivos `.env`.
- Los assets de Tailwind CSS se generan automáticamente al construir el contenedor `js-frontend`.
- El backend utiliza SQLite por defecto para desarrollo. Si agregas una base de datos o cache (Postgres, Redis), actualiza `docker-compose.yml` y las dependencias.
- Los volúmenes y persistencia de archivos no están configurados por defecto. Si necesitas persistir archivos de usuario (media), monta un volumen en `/app/media`.

---

## 🎯 Uso

1. **Admin**: `http://localhost:8000/admin/`
2. **Sistema**: `http://localhost:8000/club/`
3. **POS**: `http://localhost:8000/stock/`

## 📱 Funcionalidades por Rol

### Administrador
- Dashboard completo
- Gestión de usuarios y configuración
- Sistema de stock y ventas
- Reportes avanzados

### Recepcionista
- POS para ventas
- Gestión de reservas
- Atención al cliente

### Jugador
- Perfil personal
- Reservas propias
- Sistema de emparejamiento

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
