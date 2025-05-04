import asyncio
from twscrape import API
import pandas as pd
from pathlib import Path
from datetime import datetime

async def scrape_and_save_tweets():
    # 1. Configuración inicial
    api = API()
    
    # 2. Agregar cuenta 
    await api.pool.add_account(
        username="TestT27133",
        password="AUDI_VID3",
        email="testeoprofundo@gmail.com",
        email_password="TestTe00",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 3. Interfaz de usuario para parámetros de búsqueda
    print("\n" + "="*50)
    print("Configuración de Búsqueda de Tweets")
    print("="*50)
    
    tema = input("Ingrese el hashtag/palabra clave (ej: #Python, IA, 'machine learning'): ").strip()
    año = input("Año de búsqueda (ej: 2023, 2024): ").strip()
    idioma = input("Idioma (código de 2 letras ej: es, en, fr): ").strip() or "es"
    limite = int(input("Cantidad máxima de tweets a obtener (ej: 100): ") or 100)
    
    # NEW: Preguntar por la subcarpeta y crearla si no existe
    db_folder = Path("DB")
    db_folder.mkdir(exist_ok=True)  # Asegurar que DB existe
    
    print("\nSubcarpetas disponibles en DB:")
    subcarpetas = [d.name for d in db_folder.iterdir() if d.is_dir()]
    print(f"📂 {', '.join(subcarpetas) if subcarpetas else 'Ninguna'}")
    
    subcarpeta = input("Nombre de subcarpeta (ej: Videojuegos, Futbol) o ENTER para guardar en DB/: ").strip()
    if subcarpeta:  # Si el usuario ingresó algo
        subcarpeta_path = db_folder / subcarpeta
        subcarpeta_path.mkdir(exist_ok=True)  # Crear si no existe
        print(f"✔️ Archivo se guardará en: DB/{subcarpeta}/")
    else:
        subcarpeta_path = db_folder  # Guardar directamente en DB/
        print("✔️ Archivo se guardará en: DB/")

    # Construir query de búsqueda
    query = f"{tema} lang:{idioma} since:{año}-01-01 until:{int(año)+1}-01-01"
    
    print(f"\n🔎 Buscando: {query}")

    # 4. Scrapear y guardar
    try:
        await api.pool.login_all()
        
        # NEW: Ruta final con subcarpeta personalizada
        next_num = len(list(subcarpeta_path.glob("DB_*.xlsx"))) + 1
        filename = subcarpeta_path / f"DB_{next_num}_{tema[:20]}_{año}.xlsx"
        
        tweets = []
        async for tweet in api.search(query, limit=limite):
            tweets.append({
                "ID": tweet.id,
                "Fecha": tweet.date.strftime("%Y-%m-%d %H:%M:%S"),
                "Usuario": tweet.user.username,
                "Texto": tweet.rawContent.replace("\n", " "),
                "Likes": tweet.likeCount,
                "Retweets": tweet.retweetCount,
                "Respuestas": tweet.replyCount,
                "Idioma": idioma,
                "Tema": tema,
                "Año": año
            })
            
            if len(tweets) % 10 == 0:
                print(f"📥 Obtenidos {len(tweets)} tweets...")
        
        if tweets:
            df = pd.DataFrame(tweets)
            df.to_excel(filename, index=False)
            print(f"\n✅ {len(tweets)} tweets guardados en: {filename}")
            print(f"Muestra:\n{df.head(3)[['Fecha', 'Usuario', 'Texto']]}")
        else:
            print("⚠️ No se encontraron tweets con esos parámetros")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "login" in str(e).lower():
            print("Posible solución: Verifica tus credenciales de Twitter")

if __name__ == "__main__":
    asyncio.run(scrape_and_save_tweets())