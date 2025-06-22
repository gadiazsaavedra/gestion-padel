"""
Configuración de menús por rol de usuario
"""

MENU_CONFIG = {
    'Administrador': [
        {
            'name': 'Dashboard',
            'icon': 'fa-chart-line',
            'url': 'dashboard',
            'color': 'bg-yellow-500 hover:bg-yellow-400'
        },
        {
            'name': 'Stock & Ventas',
            'icon': 'fa-store',
            'submenu': [
                {'name': 'POS', 'url': 'stock_ventas:pos_dashboard'},
                {'name': 'Admin Stock', 'url': 'stock_ventas:dashboard_admin'},
                {'name': 'Reportes', 'url': 'stock_ventas:dashboard_reportes'},
            ]
        },
        {
            'name': 'Reservas',
            'icon': 'fa-calendar',
            'url': 'grilla_reservas',
            'color': 'bg-purple-500 hover:bg-purple-400'
        },
        {
            'name': 'Emparejamiento',
            'icon': 'fa-users',
            'url': 'panel_matchmaking',
            'color': 'bg-green-500 hover:bg-green-400'
        },
        {
            'name': 'Admin Django',
            'icon': 'fa-cogs',
            'url': 'admin:index',
            'color': 'bg-red-500 hover:bg-red-400'
        },
    ],
    
    'Recepcionista': [
        {
            'name': 'Dashboard',
            'icon': 'fa-chart-line',
            'url': 'dashboard',
            'color': 'bg-blue-500 hover:bg-blue-400'
        },
        {
            'name': 'Reservas',
            'icon': 'fa-calendar',
            'url': 'grilla_reservas',
            'color': 'bg-purple-500 hover:bg-purple-400'
        },
        {
            'name': 'Punto de Venta',
            'icon': 'fa-cash-register',
            'submenu': [
                {'name': 'POS', 'url': 'stock_ventas:pos_dashboard'},
                {'name': 'Historial Ventas', 'url': 'stock_ventas:historial_ventas'},
            ]
        },
        {
            'name': 'Emparejamiento',
            'icon': 'fa-users',
            'url': 'panel_matchmaking',
            'color': 'bg-green-500 hover:bg-green-400'
        },
    ],
    
    'Jugador': [
        {
            'name': 'Mi Panel',
            'icon': 'fa-home',
            'url': 'panel_usuario',
            'color': 'bg-green-500 hover:bg-green-400'
        },
        {
            'name': 'Mi Perfil',
            'icon': 'fa-user',
            'url': 'perfil_jugador_edit',
            'color': 'bg-blue-500 hover:bg-blue-400'
        },
        {
            'name': 'Reservas',
            'icon': 'fa-calendar',
            'url': 'grilla_reservas',
            'color': 'bg-purple-500 hover:bg-purple-400'
        },
        {
            'name': 'Emparejamiento',
            'icon': 'fa-handshake',
            'url': 'panel_matchmaking',
            'color': 'bg-orange-500 hover:bg-orange-400'
        },
        {
            'name': 'Blog',
            'icon': 'fa-newspaper',
            'url': 'blog_list',
            'color': 'bg-indigo-500 hover:bg-indigo-400'
        },
    ]
}


def get_user_menu(user):
    """Obtiene el menú correspondiente al rol del usuario"""
    if not user.is_authenticated:
        return []
    
    # Determinar rol del usuario
    if user.is_superuser:
        role = 'Administrador'
    elif user.groups.filter(name='Administrador').exists():
        role = 'Administrador'
    elif user.groups.filter(name='Recepcionista').exists():
        role = 'Recepcionista'
    elif user.groups.filter(name='Jugador').exists():
        role = 'Jugador'
    else:
        # Por defecto, usuarios normales son jugadores
        role = 'Jugador'
    
    return MENU_CONFIG.get(role, [])