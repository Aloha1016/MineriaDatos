import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from collections import Counter
import pickle

# Descargar recursos de NLTK
nltk.download('vader_lexicon')

def analizar_tendencias():
    db_folder = Path("DB")
    subcarpetas = [d.name for d in db_folder.iterdir() if d.is_dir()]

    if not subcarpetas:
        print("No se encontraron subcarpetas en DB/")
        return

    print("\n" + "="*50)
    print("CARPETAS DISPONIBLES PARA ANÁLISIS:")
    print("="*50)
    print(" " + " ".join(subcarpetas))

    carpeta_tema = input("\nIngrese el nombre de la carpeta (tema) a analizar: ").strip()
    tema_path = db_folder / carpeta_tema

    if not tema_path.exists():
        print(f"La carpeta '{carpeta_tema}' no existe en DB/")
        return

    archivos = list(tema_path.glob("DB_*.xlsx"))
    if not archivos:
        print(f"No se encontraron archivos DB_*.xlsx en {tema_path}")
        return

    dfs = []
    for archivo in archivos:
        try:
            df = pd.read_excel(archivo)
            dfs.append(df)
            print(f"Cargado: {archivo.name} ({len(df)} tweets)")
        except Exception as e:
            print(f"Error al leer {archivo.name}: {e}")

    if not dfs:
        print("No se pudieron cargar datos válidos")
        return

    datos = pd.concat(dfs, ignore_index=True)
    print("\n" + "="*50)
    print(f"REPORTE DE TENDENCIAS: {carpeta_tema.upper()}")
    print("="*50)
    print(f"Total de tweets analizados: {len(datos)}")
    print(f"Rango temporal: {datos['Fecha'].min()} a {datos['Fecha'].max()}")
    print(f"Idiomas presentes: {', '.join(datos['Idioma'].unique())}")

    datos['Fecha'] = pd.to_datetime(datos['Fecha'])
    datos['Mes'] = datos['Fecha'].dt.to_period('M')

    # Gráfico de tendencia mensual
    tendencia_mensual = datos.groupby('Mes').size()
    plt.figure(figsize=(12, 6))
    tendencia_mensual.plot(kind='line', marker='o', color='purple')
    plt.title(f'Tendencia Mensual de Tweets - {carpeta_tema}')
    plt.ylabel('Cantidad de Tweets')
    plt.grid(True)
    plt.savefig(f'tendencia_mensual_{carpeta_tema}.png')
    print(f"\n📈 Gráfico de tendencia mensual guardado como 'tendencia_mensual_{carpeta_tema}.png'")

    # Análisis de sentimientos
    analyzer = SentimentIntensityAnalyzer()
    datos['Sentimiento'] = datos['Texto'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])
    datos['Categoria_Sentimiento'] = datos['Sentimiento'].apply(
        lambda x: "Positivo" if x >= 0.05 else ("Negativo" if x <= -0.05 else "Neutral")
    )

    # Histograma de sentimientos
    plt.figure(figsize=(10, 5))
    datos['Sentimiento'].hist(bins=20, color='skyblue', edgecolor='black')
    plt.title(f'Distribución de Sentimientos - {carpeta_tema}', pad=20)
    plt.xlabel('Puntuación de Sentimiento')
    plt.ylabel('Cantidad de Tweets')
    plt.axvline(x=0.05, color='green', linestyle='--', label='Positivo')
    plt.axvline(x=-0.05, color='red', linestyle='--', label='Negativo')
    plt.legend()
    plt.savefig(f'sentimientos_{carpeta_tema}.png', bbox_inches='tight')
    print(f"📊 Gráfico de sentimientos guardado como 'sentimientos_{carpeta_tema}.png'")

    # Filtrado de jerga de internet
    jerga_internet = {
        'lol', 'omg', 'wtf', 'rofl', 'smh', 'tbh', 'btw', 'imo', 'imho', 'ftw', 
        'fyi', 'idk', 'idc', 'afaik', 'nsfw', 'tl;dr', 'dm', 'pm', 'ama', 'yolo',
        'fomo', 'tbt', 'bff', 'irl', 'icymi', 'nvm', 'oof', 'sus', 'based', 'ratio',
        'simp', 'ghost', 'clout', 'stan', 'ship', 'glowup', 'flex', 'salty', 'woke',
        'extra', 'vibe', 'mood', 'goat', 'cap', 'no cap', 'facts', 'clapback', 'snack',
        'thirsty', 'yeet', 'gatekeep', 'gaslight', 'girlboss', 'main character', 'slay',
        'periodt', 'bet', 'skrrt', 'pog', 'poggers', 'sheesh', 'rizz', 'bussin', 'mid',
        'fr', 'frfr', 'ong', 'deadass', 'bop', 'drip', 'fit', 'hits different', 'let him cook',
        'no shot', 'press f', 'say less', 'touch grass', 'w', 'l', 'skill issue', 'gg', 'ez',
        'gl', 'hf', 'wp', 'afk', 'brb', 'ggwp', 'op', 'nerf', 'buff', 'patch', 'meta',
        'report', 'troll', 'feed', 'ks', 'ksing', 'ksed', 'penta', 'quadra', 'ace'
    }

    stopwords_es = { 'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un',
                   'para', 'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 
                   'ya', 'o', 'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre',
                   'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 
                   'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e',
                   'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 
                   'él', 'tanto', 'esa', 'estos', 'mucho', 'esos', 'cada', 'ella', 'estar', 'estas', 
                   'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 
                   'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya',
                   'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros',
                   'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'es', 'son', 'era', 'eres',
                   'soy', 'está', 'están', 'estaba', 'estaban', 'fue', 'fueron' }

    def es_palabra_valida(palabra):
        return (len(palabra) > 3 and 
                not palabra.startswith(('http', '@', '#')) and 
                palabra.lower() not in stopwords_es and 
                palabra.lower() not in jerga_internet and
                palabra.isalpha())

    # Extracción de palabras positivas y negativas filtradas
    positivas = []
    negativas = []
    for texto in datos['Texto'].dropna().astype(str):
        for palabra in texto.split():
            palabra_limpia = palabra.strip(".,!?\"':;()[]{}").lower()
            if es_palabra_valida(palabra_limpia):
                score = analyzer.polarity_scores(palabra_limpia)['compound']
                if score >= 0.5:
                    positivas.append(palabra_limpia)
                elif score <= -0.5:
                    negativas.append(palabra_limpia)

    top_positivas = Counter(positivas).most_common(10)
    top_negativas = Counter(negativas).most_common(10)

    print("\nTOP PALABRAS POSITIVAS (filtradas):")
    for palabra, conteo in top_positivas:
        print(f"  {palabra}: {conteo}")

    print("\nTOP PALABRAS NEGATIVAS (filtradas):")
    for palabra, conteo in top_negativas:
        print(f"  {palabra}: {conteo}")

    # Gráfico de pastel de sentimientos
    sentimiento_counts = datos['Categoria_Sentimiento'].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(sentimiento_counts, labels=sentimiento_counts.index, autopct='%1.1f%%', startangle=140,
            colors=['lightgreen', 'lightcoral', 'lightgray'])
    plt.title(f'Comportamiento General del Tema - {carpeta_tema}')
    plt.axis('equal')
    pastel_path = f"comportamiento_pastel_{carpeta_tema}.png"
    plt.savefig(pastel_path, bbox_inches='tight')
    print(f"\n📊 Gráfico de pastel guardado como '{pastel_path}'")

    # Gráfico de caja y bigotes
    plt.figure(figsize=(10, 6))
    datos.boxplot(column='Sentimiento', by='Categoria_Sentimiento', grid=False,
                 boxprops=dict(linestyle='-', linewidth=1.5, color='purple'),
                 whiskerprops=dict(linestyle='-', linewidth=1.5, color='navy'),
                 medianprops=dict(linestyle='-', linewidth=2, color='red'),
                 capprops=dict(linestyle='-', linewidth=1.5, color='black'),
                 flierprops=dict(marker='o', markersize=3, markerfacecolor='gray'))
    
    plt.title(f'Distribución de Sentimientos - {carpeta_tema}')
    plt.suptitle('')  # Elimina el título automático
    plt.xlabel('Categoría de Sentimiento')
    plt.ylabel('Puntuación de Sentimiento')
    boxplot_path = f"boxplot_sentimientos_{carpeta_tema}.png"
    plt.savefig(boxplot_path, bbox_inches='tight')
    print(f"📦 Gráfico de caja y bigotes guardado como '{boxplot_path}'")

    # Análisis de tendencia dominante
    mayor_sentimiento = sentimiento_counts.idxmax()
    porcentaje_mayor = sentimiento_counts.max() / sentimiento_counts.sum() * 100

    if porcentaje_mayor >= 60:
        print(f"\n🔍 Existe una tendencia marcada hacia el sentimiento **{mayor_sentimiento.upper()}** ({porcentaje_mayor:.1f}%)")
    else:
        print("\n🔍 No se detecta una tendencia clara dominante en los sentimientos expresados.")

    # Nube de palabras
    texto_completo = " ".join(datos['Texto'].dropna().astype(str))
    palabras = [p.strip(".,!?\"':;()[]{}").lower() for p in texto_completo.split()]
    palabras_filtradas = [p for p in palabras if es_palabra_valida(p)]

    wordcloud = WordCloud(width=1200, height=600, background_color='white', 
                         max_words=100, colormap='plasma').generate(" ".join(palabras_filtradas))

    plt.figure(figsize=(14, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Nube de Palabras Relevantes - {carpeta_tema}', fontsize=16)
    nube_path = f"nube_palabras_{carpeta_tema}.png"
    plt.savefig(nube_path, bbox_inches='tight')
    print(f"\n☁️ Nube de palabras relevante guardada como '{nube_path}'")

    # Reporte completo
    reporte_path = f"reporte_{carpeta_tema}.txt"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(f"REPORTE COMPLETO: {carpeta_tema.upper()}\n")
        f.write("="*50 + "\n\n")
        f.write(f"Rango temporal: {datos['Fecha'].min()} a {datos['Fecha'].max()}\n")
        f.write(f"Tweets analizados: {len(datos)}\n\n")

        sentimientos = datos['Categoria_Sentimiento'].value_counts(normalize=True) * 100
        f.write("SENTIMIENTOS:\n")
        for cat, pct in sentimientos.items():
            f.write(f"  {cat}: {pct:.1f}%\n")

        f.write("\nPALABRAS POSITIVAS RELEVANTES:\n")
        for palabra, conteo in top_positivas:
            f.write(f"  {palabra}: {conteo}\n")

        f.write("\nPALABRAS NEGATIVAS RELEVANTES:\n")
        for palabra, conteo in top_negativas:
            f.write(f"  {palabra}: {conteo}\n")

        f.write("\nTENDENCIA DOMINANTE:\n")
        if porcentaje_mayor >= 60:
            f.write(f"  Existe una tendencia marcada hacia el sentimiento **{mayor_sentimiento.upper()}** ({porcentaje_mayor:.1f}%)\n")
        else:
            f.write("  No se detecta una tendencia clara dominante en los sentimientos expresados.\n")

        hashtags = Counter(
            palabra.lower() for texto in datos['Texto']
            for palabra in str(texto).split() if palabra.startswith('#')
        )
        f.write("\nTOP HASHTAGS:\n")
        for ht, cnt in hashtags.most_common(10):
            f.write(f"  #{ht}: {cnt}\n")

        datos['Engagement'] = datos['Likes'] + datos['Retweets'] * 2 + datos['Respuestas'] * 1.5
        top_tweets = datos.nlargest(5, 'Engagement')
        f.write("\nTWEETS DESTACADOS:\n")
        for _, row in top_tweets.iterrows():
            f.write(f"\n📅 {row['Fecha']} | 👤 @{row['Usuario']}\n")
            f.write(f"❤️ {row['Likes']} | 🔄 {row['Retweets']} | 💬 {row['Respuestas']}\n")
            f.write(f"📝 {row['Texto']}\n")

    print(f"\n📄 Reporte completo guardado como '{reporte_path}'")

    # Base de conocimiento mejorada
    top_hashtags = [ht for ht in hashtags.most_common(20) if not any(c.isdigit() for c in ht[0])]
    top_usuarios = Counter(
        palabra.lower() for texto in datos['Texto']
        for palabra in str(texto).split() if palabra.startswith('@')
    ).most_common(10)

    base_conocimiento = {
        'tema': carpeta_tema,
        'hashtags': top_hashtags,
        'usuarios_mencionados': top_usuarios,
        'tendencia_sentimiento': mayor_sentimiento,
        'porcentaje_dominante': porcentaje_mayor,
        'palabras_positivas': top_positivas,
        'palabras_negativas': top_negativas,
        'metricas_estadisticas': {
            'media_sentimiento': datos['Sentimiento'].mean(),
            'mediana_sentimiento': datos['Sentimiento'].median(),
            'desviacion_estandar': datos['Sentimiento'].std(),
            'rango_intercuartil': datos['Sentimiento'].quantile(0.75) - datos['Sentimiento'].quantile(0.25)
        }
    }

    conocimiento_path = f"base_conocimiento_{carpeta_tema}.pkl"
    with open(conocimiento_path, 'wb') as f:
        pickle.dump(base_conocimiento, f)
    print(f"\n💾 Base de conocimiento relevante guardada como '{conocimiento_path}'")

    print("\n" + "="*50)
    print("✅ Análisis completado con éxito!")
    print("="*50)

if __name__ == "__main__":
    analizar_tendencias()