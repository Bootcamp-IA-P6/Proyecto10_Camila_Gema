from src.news.finnhub_loader import obtener_noticias

noticias = obtener_noticias(cantidad=5)
for n in noticias:
    print("TITULAR:", n["titular"])
    print("FUENTE:", n["fuente"])
    print("RESUMEN:", n["resumen"][:150], "...")
    print("URL:", n["url"])
    print("-" * 40)