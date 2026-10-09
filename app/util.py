from math import ceil


def paginationInfo(total, pagina, porPagina):
    itemsPorPagina = porPagina if total >= porPagina else total
    totalPaginas = ceil(total / itemsPorPagina) if itemsPorPagina > 0 else 0
    paginaPrevia = pagina - 1 if pagina > 1 and pagina <= totalPaginas else None
    paginaSiguiente = pagina + 1 if totalPaginas > 1 and pagina < totalPaginas else None

    return {
        'porPagina': itemsPorPagina,
        'total': total,
        'pagina': pagina,
        'paginaPrevia': paginaPrevia,
        'paginaSiguiente': paginaSiguiente,
        'totalPaginas': totalPaginas
    }


def obtenerPaginacion(args):
    # Lee los query params page y perPage, si el cliente manda algo invalido se usan los valores por defecto
    try:
        pagina = max(int(args.get('page', 1)), 1)
    except ValueError:
        pagina = 1
    try:
        porPagina = min(max(int(args.get('perPage', 10)), 1), 100)
    except ValueError:
        porPagina = 10
    return pagina, porPagina
