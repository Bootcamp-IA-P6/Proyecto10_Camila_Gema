import os
from pyvis.network import Network

def visualizar_grafo(grafo, ruta_salida="grafo_temp.html"):
    net = Network(
        height="500px",
        width="100%",
        bgcolor="#0e1117",
        font_color="white",
        directed=True,
        notebook=False,
    )

    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=120)

    for nodo in grafo.nodes():
        grado = grafo.degree(nodo)
        tamano = 15 + grado * 4
        net.add_node(
            nodo,
            label=nodo,
            size=tamano,
            color={"background": "#ff4b4b", "border": "#ffffff"},
            font={"color": "white", "size": 14},
        )

    for origen, destino, datos in grafo.edges(data=True):
        net.add_edge(
            origen,
            destino,
            title=datos["relacion"],
            label=datos["relacion"],
            font={"color": "white", "size": 10, "strokeWidth": 0},
            arrows="to",
        )

    net.save_graph(ruta_salida)

    with open(ruta_salida, "r", encoding="utf-8") as f:
        html = f.read()

    os.remove(ruta_salida)
    return html