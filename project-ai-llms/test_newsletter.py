from src.generators.news_generator import generar_newsletter

newsletter, noticias = generar_newsletter(
    nombre_modelo="Llama 3.3 70B",
    idioma="español",
)

print("=== NEWSLETTER ===")
print(newsletter)
print("\n=== FUENTES USADAS ===")
for n in noticias:
    print(f"- {n['fuente']}: {n['titular']}")
    print(f"  {n['url']}")