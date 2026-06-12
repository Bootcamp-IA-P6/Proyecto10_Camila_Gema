from src.graph_rag.triplet_extractor import extraer_tripletas

texto = """Geoffrey Hinton es profesor en la Universidad de Toronto y ganó el premio Turing en 2018.
Hinton desarrolló el algoritmo de backpropagation y es considerado uno de los padrinos del deep learning.
Junto con Yann LeCun y Yoshua Bengio, recibió el premio por sus contribuciones a las redes neuronales profundas."""

tripletas = extraer_tripletas(texto)

print(f"Tripletas extraídas: {len(tripletas)}")
print("-" * 50)
for sujeto, relacion, objeto in tripletas:
    print(f"  {sujeto}  ──[{relacion}]──>  {objeto}")