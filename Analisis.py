import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
from PIL import Image, ImageTk
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from pathlib import Path
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from collections import Counter
import pickle
import webbrowser
import os

class TrendAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Tendencias de Twitter")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.status_var = tk.StringVar(value="Seleccione una carpeta para analizar")
        self.generated_files = []
        
        # Configuración de estilo
        self.setup_style()
        
        # Frame principal
        self.main_frame = tk.Frame(root, bg="#f5f6fa")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        self.create_title_frame()
        
        # Panel de selección
        self.create_selection_frame()
        
        # Panel de resultados
        self.results_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel de archivos generados
        self.create_files_frame()
        
        # Footer
        self.create_footer()
        
        # Precargar recursos NLTK
        self.load_nltk_resources()
    
    
    def analyze_keywords(self, datos, analyzer):
        """Analiza las palabras positivas y negativas en los tweets"""
        palabras_positivas = []
        palabras_negativas = []
        
        for texto in datos['Texto']:
            # Tokenizar y limpiar palabras
            palabras = [p.strip(".,!?\"':;()[]{}").lower() for p in str(texto).split()]
            
            for palabra in palabras:
                # Filtrar palabras no válidas
                if (len(palabra) > 3 and 
                    not palabra.startswith(('http', '@', '#')) and 
                    palabra.isalpha()):
                    
                    # Analizar sentimiento de la palabra
                    sentimiento = analyzer.polarity_scores(palabra)['compound']
                    
                    if sentimiento > 0.1:  # Umbral para positivo
                        palabras_positivas.append(palabra)
                    elif sentimiento < -0.1:  # Umbral para negativo
                        palabras_negativas.append(palabra)
        
        return palabras_positivas, palabras_negativas
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar fuentes
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=9)
        
        # Colores azul aqua en diferentes tonalidades
        style.configure('TButton', 
                    font=('Segoe UI', 10), 
                    padding=6,
                    background='#00b3b3',  
                    foreground='white',
                    bordercolor='#00838f',
                    focuscolor='#4fc3f7',
                    lightcolor='#4fc3f7',
                    darkcolor='#00838f')
        
        style.map('TButton',
                background=[('active', '#00838f'), ('pressed', '#006064')],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Estilo para botones de archivos
        style.configure('File.TButton', 
                    font=('Segoe UI', 9), 
                    padding=4, 
                    width=20,
                    background='#80deea',  
                    foreground='#004d40',
                    bordercolor='#4fb3bf')
        
        style.map('File.TButton',
                background=[('active', '#4fb3bf'), ('pressed', '#00838f')],
                foreground=[('active', 'white')])
        
        # Estilos para etiquetas
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), background="#2c3e50", foreground="white")
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), background="#2c3e50", foreground="#bdc3c7")
        style.configure('Status.TLabel', font=('Segoe UI', 10), background="#ecf0f1", foreground="#2c3e50")
    
    def create_title_frame(self):
        title_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="ANALIZADOR DE TENDENCIAS DE TWITTER", 
            style='Title.TLabel',
            padding=15
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Análisis avanzado de sentimientos y tendencias",
            style='Subtitle.TLabel',
            padding=5
        )
        subtitle_label.pack()
    
    def create_selection_frame(self):
        selection_frame = tk.Frame(self.main_frame, bg="#ecf0f1", padx=20, pady=20)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Etiqueta
        tk.Label(
            selection_frame,
            text="Seleccionar carpeta de análisis:",
            font=("Segoe UI", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).grid(row=0, column=0, padx=5, sticky='w')
        
        # Entry para la carpeta
        folder_entry = ttk.Entry(
            selection_frame,
            textvariable=self.selected_folder,
            font=("Segoe UI", 10),
            width=40
        )
        folder_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        # Botón para buscar
        browse_btn = ttk.Button(
            selection_frame,
            text="Examinar",
            command=self.browse_folder,
            style='TButton'
        )
        browse_btn.grid(row=0, column=2, padx=5)
        
        # Botón de análisis
        analyze_btn = ttk.Button(
            selection_frame,
            text="Analizar Tendencias",
            command=self.start_analysis,
            style='TButton'
        )
        analyze_btn.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')
        
        # Barra de estado
        status_label = ttk.Label(
            selection_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            anchor='w'
        )
        status_label.grid(row=2, column=0, columnspan=3, sticky='ew')
        
        selection_frame.grid_columnconfigure(1, weight=1)
    
    def create_files_frame(self):
        files_frame = tk.Frame(self.main_frame, bg="#ecf0f1", padx=20, pady=20)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            files_frame,
            text="ARCHIVOS GENERADOS",
            font=("Segoe UI", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        # Frame para los botones de archivos
        self.files_buttons_frame = tk.Frame(files_frame, bg="#ecf0f1")
        self.files_buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para la visualización de imágenes
        self.image_frame = tk.Frame(files_frame, bg="#ecf0f1", height=400)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Etiqueta para la imagen
        self.image_label = tk.Label(self.image_frame, bg="#ecf0f1")
        self.image_label.pack(fill=tk.BOTH, expand=True)
    
    def create_footer(self):
        footer = tk.Label(
            self.main_frame,
            text="© 2025 Analizador de Tendencias | Díaz Segovia D.",
            font=("Segoe UI", 8),
            fg="#95a5a6",
            bg="#f5f6fa"
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
    def load_nltk_resources(self):
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.status_var.set("Recursos NLTK cargados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los recursos NLTK: {str(e)}")
    
    def browse_folder(self):
        initial_dir = Path("DB")
        if not initial_dir.exists():
            initial_dir.mkdir()
        
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de análisis",
            initialdir=str(initial_dir))
        
        if folder:
            self.selected_folder.set(folder)
    
    def start_analysis(self):
        if not self.selected_folder.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione una carpeta para analizar")
            return
        
        tema_path = Path(self.selected_folder.get())
        if not tema_path.exists():
            messagebox.showerror("Error", f"La carpeta '{tema_path}' no existe")
            return
        
        # Limpiar resultados anteriores
        for widget in self.files_buttons_frame.winfo_children():
            widget.destroy()
        
        self.generated_files = []
        self.status_var.set(f"Analizando carpeta: {tema_path.name}...")
        self.root.update()
        
        try:
            # Ejecutar el análisis en un hilo separado para no bloquear la interfaz
            import threading
            threading.Thread(target=self.run_analysis, args=(tema_path,), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el análisis: {str(e)}")
    
    def run_analysis(self, tema_path):
        try:
            archivos = list(tema_path.glob("DB_*.xlsx"))
            if not archivos:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Advertencia", 
                    f"No se encontraron archivos DB_*.xlsx en {tema_path}"))
                return
            
            dfs = []
            for archivo in archivos:
                try:
                    df = pd.read_excel(archivo)
                    dfs.append(df)
                    self.root.after(0, lambda: self.status_var.set(
                        f"Cargando: {archivo.name} ({len(df)} tweets)"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Advertencia", 
                        f"Error al leer {archivo.name}: {e}"))
            
            if not dfs:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "No se pudieron cargar datos válidos"))
                return
            
            datos = pd.concat(dfs, ignore_index=True)
            carpeta_tema = tema_path.name
                        
            self.root.after(0, lambda: self.perform_analysis(datos, carpeta_tema))
            
            # Mostrar botones para los archivos generados
            self.root.after(0, self.display_generated_files)
            
            self.root.after(0, lambda: self.status_var.set(
                f"✅ Análisis completado para {carpeta_tema}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error durante el análisis: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(
                f"❌ Error al analizar {tema_path.name}"))
    
    def perform_analysis(self, datos, carpeta_tema):        
        # Configurar Fecha y Mes
        datos['Fecha'] = pd.to_datetime(datos['Fecha'])
        datos['Mes'] = datos['Fecha'].dt.to_period('M')
        
        # Análisis de sentimientos
        analyzer = SentimentIntensityAnalyzer()
        datos['Sentimiento'] = datos['Texto'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])
        datos['Categoria_Sentimiento'] = datos['Sentimiento'].apply(
            lambda x: "Positivo" if x >= 0.05 else ("Negativo" if x <= -0.05 else "Neutral")
        )
        
        # 1. Gráfico de tendencia mensual
        tendencia_mensual = datos.groupby('Mes').size()
        plt.figure(figsize=(12, 6))
        tendencia_mensual.plot(kind='line', marker='o', color='purple')
        plt.title(f'Tendencia Mensual de Tweets - {carpeta_tema}')
        plt.ylabel('Cantidad de Tweets')
        plt.grid(True)
        tendencia_path = f'tendencia_mensual_{carpeta_tema}.png'
        plt.savefig(tendencia_path)
        plt.close()
        self.generated_files.append(("📈 Tendencia Mensual", tendencia_path))
        
        # 2. Histograma de sentimientos
        plt.figure(figsize=(10, 5))
        datos['Sentimiento'].hist(bins=20, color='skyblue', edgecolor='black')
        plt.title(f'Distribución de Sentimientos - {carpeta_tema}', pad=20)
        plt.xlabel('Puntuación de Sentimiento')
        plt.ylabel('Cantidad de Tweets')
        plt.axvline(x=0.05, color='green', linestyle='--', label='Positivo')
        plt.axvline(x=-0.05, color='red', linestyle='--', label='Negativo')
        plt.legend()
        sentimientos_path = f'sentimientos_{carpeta_tema}.png'
        plt.savefig(sentimientos_path, bbox_inches='tight')
        plt.close()
        self.generated_files.append(("📊 Histograma Sentimientos", sentimientos_path))
        
        # 3. Gráfico de pastel de sentimientos
        sentimiento_counts = datos['Categoria_Sentimiento'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(sentimiento_counts, labels=sentimiento_counts.index, autopct='%1.1f%%', startangle=140,
                colors=['lightgreen', 'lightcoral', 'lightgray'])
        plt.title(f'Comportamiento General del Tema - {carpeta_tema}')
        plt.axis('equal')
        pastel_path = f"comportamiento_pastel_{carpeta_tema}.png"
        plt.savefig(pastel_path, bbox_inches='tight')
        plt.close()
        self.generated_files.append(("📊 Pastel Sentimientos", pastel_path))
        
        # 4. Gráfico de caja y bigotes
        plt.figure(figsize=(10, 6))
        datos.boxplot(column='Sentimiento', by='Categoria_Sentimiento', grid=False,
                     boxprops=dict(linestyle='-', linewidth=1.5, color='purple'),
                     whiskerprops=dict(linestyle='-', linewidth=1.5, color='navy'),
                     medianprops=dict(linestyle='-', linewidth=2, color='red'),
                     capprops=dict(linestyle='-', linewidth=1.5, color='black'),
                     flierprops=dict(marker='o', markersize=3, markerfacecolor='gray'))
        plt.title(f'Distribución de Sentimientos - {carpeta_tema}')
        plt.suptitle('')
        plt.xlabel('Categoría de Sentimiento')
        plt.ylabel('Puntuación de Sentimiento')
        boxplot_path = f"boxplot_sentimientos_{carpeta_tema}.png"
        plt.savefig(boxplot_path, bbox_inches='tight')
        plt.close()
        self.generated_files.append(("📦 Caja y Bigotes", boxplot_path))
        
        # 5. Nube de palabras
        texto_completo = " ".join(datos['Texto'].dropna().astype(str))
        palabras = [p.strip(".,!?\"':;()[]{}").lower() for p in texto_completo.split()]
        
        # Filtrado de palabras (similar a tu función original)
        jerga_internet = {'lol', 'omg', 'wtf', 'rofl', 'smh', 'tbh', 'btw', 'imo', 'imho', 'ftw'}
        stopwords_es = {'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se'}
        
        def es_palabra_valida(palabra):
            return (len(palabra) > 3 and 
                    not palabra.startswith(('http', '@', '#')) and 
                    palabra.lower() not in stopwords_es and 
                    palabra.lower() not in jerga_internet and
                    palabra.isalpha())
        
        palabras_filtradas = [p for p in palabras if es_palabra_valida(p)]
        
        wordcloud = WordCloud(width=1200, height=600, background_color='white', 
                             max_words=100, colormap='plasma').generate(" ".join(palabras_filtradas))
        
        plt.figure(figsize=(14, 7))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Nube de Palabras Relevantes - {carpeta_tema}', fontsize=16)
        nube_path = f"nube_palabras_{carpeta_tema}.png"
        plt.savefig(nube_path, bbox_inches='tight')
        plt.close()
        self.generated_files.append(("☁️ Nube de Palabras", nube_path))
        
        # 6. Reporte completo
        reporte_path = f"reporte_{carpeta_tema}.txt"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(f"REPORTE COMPLETO: {carpeta_tema.upper()}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Rango temporal: {datos['Fecha'].min()} a {datos['Fecha'].max()}\n")
            f.write(f"Tweets analizados: {len(datos)}\n\n")

            # Estadísticas de sentimientos
            sentimientos = datos['Categoria_Sentimiento'].value_counts(normalize=True) * 100
            f.write("SENTIMIENTOS:\n")
            for cat, pct in sentimientos.items():
                f.write(f"  {cat}: {pct:.1f}%\n")

            # Palabras positivas y negativas
            positivas, negativas = self.analyze_keywords(datos, analyzer)
            top_positivas = Counter(positivas).most_common(10)
            top_negativas = Counter(negativas).most_common(10)

            f.write("\nPALABRAS POSITIVAS RELEVANTES:\n")
            for palabra, conteo in top_positivas:
                f.write(f"  {palabra}: {conteo}\n")

            f.write("\nPALABRAS NEGATIVAS RELEVANTES:\n")
            for palabra, conteo in top_negativas:
                f.write(f"  {palabra}: {conteo}\n")

            # Tendencia dominante
            sentimiento_counts = datos['Categoria_Sentimiento'].value_counts()
            mayor_sentimiento = sentimiento_counts.idxmax()
            porcentaje_mayor = sentimiento_counts.max() / sentimiento_counts.sum() * 100

            f.write("\nTENDENCIA DOMINANTE:\n")
            if porcentaje_mayor >= 60:
                f.write(f"  Existe una tendencia marcada hacia el sentimiento **{mayor_sentimiento.upper()}** ({porcentaje_mayor:.1f}%)\n")
            else:
                f.write("  No se detecta una tendencia clara dominante en los sentimientos expresados.\n")

            # Hashtags más usados
            hashtags = Counter(
                palabra.lower() for texto in datos['Texto']
                for palabra in str(texto).split() if palabra.startswith('#')
            )
            f.write("\nTOP HASHTAGS:\n")
            for ht, cnt in hashtags.most_common(10):
                f.write(f"  #{ht}: {cnt}\n")

            # Tweets con mayor engagement
            datos['Engagement'] = datos['Likes'] + datos['Retweets'] * 2 + datos['Respuestas'] * 1.5
            top_tweets = datos.nlargest(5, 'Engagement')
            f.write("\nTWEETS DESTACADOS:\n")
            for _, row in top_tweets.iterrows():
                f.write(f"\n📅 {row['Fecha']} | 👤 @{row['Usuario']}\n")
                f.write(f"❤️ {row['Likes']} | 🔄 {row['Retweets']} | 💬 {row['Respuestas']}\n")
                f.write(f"📝 {row['Texto']}\n")

        self.generated_files.append(("📄 Reporte Completo", reporte_path))
        
        # 7. Base de conocimiento
        conocimiento_path = f"base_conocimiento_{carpeta_tema}.pkl"
    
        # Hashtags filtrados
        top_hashtags = [ht for ht in hashtags.most_common(20) if not any(c.isdigit() for c in ht[0])]
        
        # Usuarios más mencionados
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
            },
            'tweets_destacados': [
                {
                    'fecha': str(row['Fecha']),
                    'usuario': row['Usuario'],
                    'texto': row['Texto'],
                    'likes': row['Likes'],
                    'retweets': row['Retweets'],
                    'respuestas': row['Respuestas'],
                    'engagement': row['Engagement']
                }
                for _, row in top_tweets.iterrows()
            ]
        }

        with open(conocimiento_path, 'wb') as f:
            pickle.dump(base_conocimiento, f)
        self.generated_files.append(("💾 Base de Conocimiento", conocimiento_path))
    
    def display_generated_files(self):
        # Limpiar frame de botones
        for widget in self.files_buttons_frame.winfo_children():
            widget.destroy()
        
        # Limpiar imagen actual
        self.clear_image()
        
        # Mostrar botones para cada archivo generado
        for i, (name, path) in enumerate(self.generated_files):
            btn = ttk.Button(
                self.files_buttons_frame,
                text=name,
                command=lambda p=path: self.show_file(p),
                style='File.TButton'
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        # Ajustar columnas
        for i in range(3):
            self.files_buttons_frame.grid_columnconfigure(i, weight=1)
    
    def show_file(self, filepath):
        if filepath.endswith(('.png', '.jpg', '.jpeg')):
            self.display_image(filepath)
        elif filepath.endswith('.txt'):
            self.open_text_file(filepath)
        elif filepath.endswith('.pkl'):
            messagebox.showinfo(
                "Base de Conocimiento", 
                "Este es un archivo binario que contiene los resultados del análisis.")
        else:
            webbrowser.open(filepath)
    
    def display_image(self, image_path):
        try:
            self.clear_image()
            
            img = Image.open(image_path)
            # Redimensionar manteniendo aspect ratio
            max_width = self.image_frame.winfo_width() - 20
            max_height = self.image_frame.winfo_height() - 20
            
            if img.width > max_width or img.height > max_height:
                ratio = min(max_width/img.width, max_height/img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Mantener referencia
            
            # Botón para abrir imagen completa
            open_btn = ttk.Button(
                self.image_frame,
                text="Abrir imagen completa",
                command=lambda: self.open_image_full(image_path),
                style='TButton'
            )
            open_btn.place(relx=0.5, rely=0.95, anchor='center')
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def clear_image(self):
        self.image_label.config(image='')
        for widget in self.image_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
    
    def open_image_full(self, image_path):
        try:
            img = Image.open(image_path)
            img.show()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen: {str(e)}")
    
    def open_text_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Crear ventana emergente para mostrar el texto
            text_window = tk.Toplevel(self.root)
            text_window.title(f"Contenido: {Path(filepath).name}")
            text_window.geometry("800x600")
            
            text_frame = tk.Frame(text_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_area = tk.Text(
                text_frame,
                wrap=tk.WORD,
                yscrollcommand=scrollbar.set,
                font=("Consolas", 10)
            )
            text_area.pack(fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_area.yview)
            
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            
            # Botón para cerrar
            close_btn = ttk.Button(
                text_window,
                text="Cerrar",
                command=text_window.destroy
            )
            close_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Centrar la ventana
    window_width = 1000
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    app = TrendAnalysisApp(root)
    root.mainloop()