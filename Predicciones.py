import pickle
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from difflib import SequenceMatcher
from collections import defaultdict

nltk.download('all', halt_on_error=False)

def configurar_nltk():
    try:
        # Verificar y descargar recursos necesarios
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        # Descargar datos específicos para español
        try:
            nltk.data.find('tokenizers/punkt/spanish.pickle')
        except LookupError:
            nltk.download('punkt', quiet=True)
            # Para español necesitamos descargar el paquete adicional
            nltk.download('cess_esp', quiet=True)  # Corpus español para entrenar el tokenizador
        
        # Cargar stopwords en español
        nltk.download('stopwords', quiet=True)
        
    except Exception as e:
        print(f"Error configurando NLTK: {str(e)}")
        raise

configurar_nltk()

analyzer = SentimentIntensityAnalyzer()

# Plantillas para generar ideas más elaboradas
PLANTILLAS_IDEAS = [
    "El impacto de {concepto} en {contexto}",
    "Cómo {concepto} está cambiando {contexto}",
    "La relación entre {concepto} y {contexto}",
    "Tendencias emergentes en {concepto} para {contexto}",
    "Por qué {concepto} es importante para {contexto}",
    "El futuro de {concepto} en el ámbito de {contexto}",
    "{concepto}: una nueva perspectiva sobre {contexto}",
    "Desafíos y oportunidades de {concepto} en {contexto}"
]

CONTEXTOS = [
    "la sociedad actual", "las redes sociales", "la política moderna",
    "la economía digital", "la cultura juvenil", "la tecnología emergente",
    "las discusiones públicas", "el ámbito empresarial", "la educación",
    "las relaciones internacionales", "el medio ambiente"
]

def cargar_base_conocimiento(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def generar_ideas_estructuradas(base):
    print("\n💡 POSIBLES TENDENCIAS Y TEMAS DE DISCUSIÓN:")
    
    # Extraer componentes clave
    hashtags = [h[0].strip('#') for h in base['hashtags'] if not any(c.isdigit() for c in h[0])]
    usuarios = [u[0].strip('@') for u in base['usuarios_mencionados']]
    palabras_clave = [w[0] for w in base['palabras_positivas'][:7]] + [w[0] for w in base['palabras_negativas'][:7]]
    
    # Filtrar elementos vacíos o muy cortos
    palabras_clave = [p for p in palabras_clave if len(p) > 3 and p.isalpha()]
    hashtags = [h for h in hashtags if len(h) > 3 and h.isalpha()]
    
    # Agrupar palabras por categorías (simplificado)
    categorias = defaultdict(list)
    for palabra in palabras_clave:
        if palabra.endswith(('ción', 'sión', 'miento', 'anza')):
            categorias['conceptos'].append(palabra)
        elif palabra.endswith(('ar', 'er', 'ir')):
            categorias['acciones'].append(palabra)
        else:
            categorias['sustantivos'].append(palabra)
    
    # Generar ideas combinando componentes
    ideas_generadas = set()
    for _ in range(8):
        try:
            plantilla = random.choice(PLANTILLAS_IDEAS)
            contexto = random.choice(CONTEXTOS)
            
            # Seleccionar concepto según la plantilla
            if "{concepto}" in plantilla:
                if random.random() > 0.5 and categorias['conceptos']:
                    concepto = random.choice(categorias['conceptos'])
                elif hashtags:
                    concepto = random.choice(hashtags)
                else:
                    concepto = random.choice(palabras_clave)
                
                # Capitalizar correctamente
                concepto = concepto.capitalize()
                
                idea = plantilla.format(concepto=concepto, contexto=contexto)
                ideas_generadas.add(idea)
        except:
            continue
    
    # Si no se generaron suficientes ideas, completar con combinaciones simples
    while len(ideas_generadas) < 5 and palabras_clave and hashtags:
        p1 = random.choice(palabras_clave)
        p2 = random.choice(hashtags)
        ideas_generadas.add(f"¿Cómo afectará {p1} a {p2} en el futuro cercano?")
    
    # Mostrar ideas numeradas
    for i, idea in enumerate(sorted(ideas_generadas, key=lambda x: len(x)), 1):
        print(f"{i}. {idea}")

def evaluar_idea_compleja(idea, base):
    idea = idea.lower()
    
    try:
        # Componentes de análisis mejorado
        hashtags = [h[0].lower() for h in base['hashtags']]
        usuarios = [u[0].lower() for u in base['usuarios_mencionados']]
        palabras_clave = [w[0].lower() for w in base['palabras_positivas'] + base['palabras_negativas']]
        
        # 1. Análisis de relevancia
        palabras_idea = set(nltk.word_tokenize(idea, language='spanish'))
        palabras_idea.difference_update(set(nltk.corpus.stopwords.words('spanish')))
        
        # Calcular coincidencias con elementos conocidos
        matches_hashtags = sum(1 for h in hashtags if any(SequenceMatcher(None, h, p).ratio() > 0.7 for p in palabras_idea))
        matches_palabras = sum(1 for p in palabras_idea if p in palabras_clave)
        matches_usuarios = sum(1 for u in usuarios if any(u in p for p in palabras_idea))
        
        # Ponderar los diferentes componentes
        relevancia = (
            0.4 * min(matches_palabras / 5, 1.0) + 
            0.3 * min(matches_hashtags / 3, 1.0) + 
            0.2 * min(matches_usuarios / 2, 1.0) + 
            0.1 * (1 if any(p in idea for p in ['futuro', 'tendencia', 'impacto', 'cambio']) else 0)
        )
        
        # 2. Análisis de sentimiento compuesto
        sentimiento = analyzer.polarity_scores(idea)['compound']
        
        # 3. Análisis de novedad (simplificado)
        palabras_nuevas = sum(1 for p in palabras_idea if p not in palabras_clave and len(p) > 4)
        novedad = min(palabras_nuevas / 3, 1.0)
        
        # Calcular puntuación final
        puntuacion = round((relevancia * 0.6 + novedad * 0.2 + (sentimiento + 1) * 0.2) * 100, 2)
        
        # Determinar recepción estimada
        if sentimiento >= 0.15:
            recepcion = "Muy positiva"
        elif sentimiento >= 0.05:
            recepcion = "Positiva"
        elif sentimiento <= -0.15:
            recepcion = "Muy negativa"
        elif sentimiento <= -0.05:
            recepcion = "Negativa"
        else:
            recepcion = "Neutral"
        
        # Generar recomendación
        if puntuacion > 75:
            recomendacion = "✅ Excelente tema con alta probabilidad de convertirse en tendencia"
        elif puntuacion > 50:
            recomendacion = "👍 Buen tema con potencial de crecimiento"
        else:
            recomendacion = "🤔 Tema interesante pero puede necesitar más desarrollo"
        
        # Mostrar resultados detallados
        print("\n🔍 ANÁLISIS COMPLETO DE LA IDEA:")
        print(f"Tema analizado: '{idea.capitalize()}'")
        print(f"\n📊 Puntuación de tendencia: {puntuacion:.2f}/100")
        print(f"   - Relevancia histórica: {relevancia*100:.2f}%")
        print(f"   - Novedad: {novedad*100:.2f}%")
        print(f"   - Sentimiento público: {recepcion} ({sentimiento:.2f})")
        print(f"\n💡 Recomendación: {recomendacion}")
        
        # Sugerencias de mejora
        if matches_palabras < 2:
            print("\n🔧 Sugerencia: Considera incluir más palabras clave relevantes")
        if matches_hashtags == 0:
            print("🔧 Sugerencia: Relaciona con hashtags populares del tema")
        if novedad < 0.3:
            print("🔧 Sugerencia: Añade elementos innovadores o de actualidad")
    
    except Exception as e:
        print(f"⚠️ Error al analizar la idea: {str(e)}")
        print("Por favor, intenta con otra idea o verifica la configuración de NLTK")

def main():
    archivo = input("Ingrese el nombre del archivo de base de conocimiento (ej. base_conocimiento_tema.pkl): ").strip()
    
    try:
        base = cargar_base_conocimiento(archivo)
        print(f"\n📂 Base de conocimiento cargada: {base['tema'].upper()}")
        print(f"   - Hashtags relevantes: {', '.join([h[0] for h in base['hashtags'][:5]])}...")
        print(f"   - Palabras clave: {', '.join([w[0] for w in base['palabras_positivas'][:3] + base['palabras_negativas'][:3]])}...")
    except Exception as e:
        print(f"❌ Error al cargar la base de conocimiento: {e}")
        return

    generar_ideas_estructuradas(base)

    while True:
        idea = input("\n📝 Ingresa un tema para analizar (o 'salir' para terminar): ").strip()
        if idea.lower() == 'salir':
            break
        if len(idea.split()) < 3:
            print("⚠️ Por favor, ingresa una idea más elaborada (mínimo 3 palabras)")
            continue
        evaluar_idea_compleja(idea, base)

if __name__ == "__main__":
    main()