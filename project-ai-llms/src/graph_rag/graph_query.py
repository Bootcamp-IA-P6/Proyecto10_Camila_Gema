def buscar_entidades_en_grafo(grafo, termino):
    termino_lower = termino.lower()
    return [nodo for nodo in grafo.nodes() if termino_lower in nodo.lower()]


def obtener_contexto_de_entidad(grafo, entidad, profundidad=1):
    contexto = []
    visitados = {entidad}

    # Aristas salientes: cosas que la entidad "hace"
    for _, destino, datos in grafo.out_edges(entidad, data=True):
        contexto.append(f"{entidad} {datos['relacion']} {destino}")
        visitados.add(destino)

    # Aristas entrantes: cosas que se relacionan con la entidad
    for origen, _, datos in grafo.in_edges(entidad, data=True):
        contexto.append(f"{origen} {datos['relacion']} {entidad}")
        visitados.add(origen)

    # Si profundidad > 1, exploramos los vecinos de los vecinos
    if profundidad > 1:
        for vecino in list(visitados - {entidad}):
            for _, destino, datos in grafo.out_edges(vecino, data=True):
                if destino not in visitados:
                    contexto.append(f"{vecino} {datos['relacion']} {destino}")

    return contexto


def consultar_grafo(grafo, terminos_busqueda, profundidad=1):
    contexto_total = []
    entidades_encontradas = []

    for termino in terminos_busqueda:
        entidades = buscar_entidades_en_grafo(grafo, termino)
        for entidad in entidades:
            entidades_encontradas.append(entidad)
            contexto = obtener_contexto_de_entidad(grafo, entidad, profundidad)
            contexto_total.extend(contexto)

    # Eliminar duplicados manteniendo el orden
    contexto_unico = list(dict.fromkeys(contexto_total))
    return {
        "entidades_encontradas": list(set(entidades_encontradas)),
        "contexto": contexto_unico,
    }