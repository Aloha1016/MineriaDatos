# Scraping y Análisis de Comportamiento de Usuarios

Este proyecto permite realizar scraping de datos desde Twitter y analizar el comportamiento de los usuarios usando interfaces gráficas interactivas. Incluye visualizaciones, análisis de sentimientos, y generación de nubes de palabras.

## Funcionalidades

- Interfaz gráfica basada en `tkinter`.
- Scraping de Twitter mediante `twscrape`.
- Visualización de estadísticas con `matplotlib`.
- Análisis de sentimientos con `nltk`.
- Generación de nubes de palabras con `wordcloud`.
- Visualización de imágenes y gráficos.
- Almacenamiento y carga de datos procesados.

## Requisitos

- Python 3.8 o superior

## Instalación

1. Clona el repositorio o descarga los archivos del proyecto.
2. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate     # En Linux/macOS
   venv\Scripts\activate        # En Windows

3. Instala las dependencias necesarias 

    pip install -r requirements.txt

4. Instala el procesador de lenguaje NLTK

    import nltk
    nltk.download('vader_lexicon')

## Recomendación

Ejecuta el codigo 'Menu.py' para acceder a los otros modulos de manera interactiva.
O ejecuta cada modulo de manera independiente.

## Base de Datos

No se subió la base de datos para que el usuario pueda crear sus propias colecciones según temas de interés personal.
