from club.models import Jugador, DisponibilidadJugador
from itertools import combinations
from django.db.models import Q


def buscar_grupos(
    nivel, genero, dia=None, hora_inicio=None, hora_fin=None, max_grupos=5
):
    """
    Devuelve una lista de grupos posibles (listas de 4 jugadores compatibles) usando DisponibilidadJugador.
    Si se especifica día y franja horaria, filtra por superposición horaria.
    """
    # Filtrar jugadores activos con disponibilidad cargada
    jugadores = Jugador.objects.filter(nivel=nivel, genero=genero, en_tinder=True)
    # Buscar disponibilidades compatibles
    disponibilidades = DisponibilidadJugador.objects.filter(
        jugador__in=jugadores,
        nivel=nivel,
        preferencia_genero=genero,
    )
    if dia:
        disponibilidades = disponibilidades.filter(dia=dia)
    # Agrupar por jugador
    disp_por_jugador = {}
    for d in disponibilidades:
        disp_por_jugador.setdefault(d.jugador, []).append(d)
    compatibles = list(disp_por_jugador.keys())
    grupos = []
    ids_set = set()
    for grupo in combinations(compatibles, 4):
        # Buscar intersección de horarios si se especifica
        if dia and (hora_inicio or hora_fin):
            horas = [
                (
                    min([d.hora_inicio for d in disp_por_jugador[j] if d.dia == dia]),
                    max([d.hora_fin for d in disp_por_jugador[j] if d.dia == dia]),
                )
                for j in grupo
            ]
            max_inicio = max(h[0] for h in horas)
            min_fin = min(h[1] for h in horas)
            if min_fin <= max_inicio:
                continue  # No hay superposición
        grupo_ids = tuple(sorted(j.id for j in grupo))
        if grupo_ids not in ids_set:
            grupos.append(grupo)
            ids_set.add(grupo_ids)
        if len(grupos) >= max_grupos:
            break
    return grupos


def sugerir_grupos():
    """
    Wrapper para buscar_grupos con parámetros de ejemplo para los tests.
    Devuelve grupos de 4 jugadores con nivel intermedio, género hombre y disponibilidad lunes 18:00.
    """
    nivel = "intermedio"
    genero = "hombre"
    dia = "lunes"
    grupos_tuplas = buscar_grupos(nivel, genero, dia=dia, max_grupos=5)
    return [
        type(
            "GrupoMock",
            (),
            {
                "jugadores": lambda self, jugadores=grupo: type(
                    "J", (), {"all": lambda s: jugadores}
                )()
            },
        )()
        for grupo in grupos_tuplas
    ]
