"""
Configuración de menús por rol de usuario
"""

MENU_CONFIG = {
    "Administrador": [
        {
            "name": "Panel",
            "icon": "fa-chart-bar",
            "url": "dashboard",
            "color": "bg-green-500 hover:bg-green-400",
        },
        {
            "name": "Jugadores",
            "icon": "fa-users",
            "url": "jugadores:list",
            "color": "bg-blue-500 hover:bg-blue-400",
        },
        {
            "name": "Reservas",
            "icon": "fa-calendar",
            "url": "grilla_reservas",
            "color": "bg-blue-600 hover:bg-blue-500",
        },
        {
            "name": "Pagos",
            "icon": "fa-credit-card",
            "url": "admin:index",
            "color": "bg-yellow-500 hover:bg-yellow-400",
        },
        {
            "name": "Torneos",
            "icon": "fa-trophy",
            "url": "torneos_list",
            "color": "bg-red-500 hover:bg-red-400",
        },
        {
            "name": "POS/Bar",
            "icon": "fa-shopping-cart",
            "url": "stock_ventas:pos_dashboard",
            "color": "bg-green-600 hover:bg-green-500",
        },
        {
            "name": "Stock",
            "icon": "fa-boxes",
            "url": "stock_ventas:dashboard_admin",
            "color": "bg-yellow-600 hover:bg-yellow-500",
        },
        {
            "name": "Reportes",
            "icon": "fa-chart-line",
            "url": "stock_ventas:dashboard_reportes",
            "color": "bg-green-500 hover:bg-green-400",
        },
        {
            "name": "Emparejamiento",
            "icon": "fa-handshake",
            "url": "panel_matchmaking",
            "color": "bg-red-700 hover:bg-red-600",
        },
        {
            "name": "Admin Django",
            "icon": "fa-cogs",
            "url": "admin:index",
            "color": "bg-red-600 hover:bg-red-500",
        },
        {
            "name": "Finanzas",
            "icon": "fa-money-bill-wave",
            "submenu": [
                {"name": "Empleados", "url": "admin:club_empleado_changelist"},
                {"name": "Pagos Empleados", "url": "admin:club_pagoempleado_changelist"},
                {"name": "Proveedores", "url": "admin:club_proveedor_changelist"},
                {"name": "Pagos Proveedores", "url": "admin:club_pagoproveedor_changelist"},
                {"name": "Servicios Públicos", "url": "admin:club_serviciopublico_changelist"},
                {"name": "Pagos Servicios", "url": "admin:club_pagoservicio_changelist"},
                {"name": "Impuestos", "url": "admin:club_impuesto_changelist"},
            ],
        },
        {
            "name": "Configuración",
            "icon": "fa-sliders-h",
            "url": "homepage",
            "color": "bg-green-700 hover:bg-green-600",
        },
    ],
    "Recepcionista": [
        {
            "name": "Dashboard",
            "icon": "fa-chart-line",
            "url": "dashboard",
            "color": "bg-blue-500 hover:bg-blue-400",
        },
        {
            "name": "Reservas",
            "icon": "fa-calendar",
            "url": "grilla_reservas",
            "color": "bg-purple-500 hover:bg-purple-400",
        },
        {
            "name": "Punto de Venta",
            "icon": "fa-cash-register",
            "submenu": [
                {"name": "POS", "url": "stock_ventas:pos_dashboard"},
                {"name": "Historial Ventas", "url": "stock_ventas:historial_ventas"},
            ],
        },
        {
            "name": "Emparejamiento",
            "icon": "fa-users",
            "url": "panel_matchmaking",
            "color": "bg-green-500 hover:bg-green-400",
        },
    ],
    "Jugador": [
        {
            "name": "Mi Panel",
            "icon": "fa-home",
            "url": "panel_usuario",
            "color": "bg-green-500 hover:bg-green-400",
        },
        {
            "name": "Mi Perfil",
            "icon": "fa-user",
            "url": "perfil_jugador_edit",
            "color": "bg-blue-500 hover:bg-blue-400",
        },
        {
            "name": "Reservas",
            "icon": "fa-calendar",
            "url": "grilla_reservas",
            "color": "bg-purple-500 hover:bg-purple-400",
        },
        {
            "name": "Emparejamiento",
            "icon": "fa-handshake",
            "url": "panel_matchmaking",
            "color": "bg-orange-500 hover:bg-orange-400",
        },
        {
            "name": "Blog",
            "icon": "fa-newspaper",
            "url": "blog_list",
            "color": "bg-indigo-500 hover:bg-indigo-400",
        },
    ],
}


def get_user_menu(user):
    """Obtiene el menú correspondiente al rol del usuario"""
    if not user.is_authenticated:
        return []

    # Determinar rol del usuario
    if user.is_superuser:
        role = "Administrador"
    elif user.groups.filter(name="Administrador").exists():
        role = "Administrador"
    elif user.groups.filter(name="Recepcionista").exists():
        role = "Recepcionista"
    elif user.groups.filter(name="Jugador").exists():
        role = "Jugador"
    else:
        # Por defecto, usuarios normales son jugadores
        role = "Jugador"

    return MENU_CONFIG.get(role, [])