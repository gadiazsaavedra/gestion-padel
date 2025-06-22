from .menu_config import get_user_menu


def menu_context(request):
    """Context processor para agregar menú dinámico a todos los templates"""
    return {
        'user_menu': get_user_menu(request.user) if hasattr(request, 'user') else []
    }