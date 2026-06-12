from src.image_search import buscar_imagenes

resultado = buscar_imagenes("café", cantidad=3)
for img in resultado:
    print(img)