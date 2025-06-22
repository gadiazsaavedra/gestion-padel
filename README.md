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