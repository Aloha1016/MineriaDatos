import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pickle
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from difflib import SequenceMatcher
from collections import defaultdict
import threading
from tkinter import font as tkfont

class TrendAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Tendencias en Redes Sociales")
        self.root.geometry("900x750+100+100")
        self.root.resizable(False, False)
        
        # Variables
        self.base_conocimiento = None
        self.loading = False
        
        # Configurar estilo
        self.setup_styles()
        
        # Configurar NLTK en segundo plano
        threading.Thread(target=self.configurar_nltk, daemon=True).start()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar la ventana
        self.center_window()
    
    def center_window(self):
        window_width = 900
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    def setup_styles(self):
        # Configurar fuentes
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=9)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family="Segoe UI", size=9)
        
        # Paleta de colores
        self.colors = {
            'header_bg': '#2c3e50',
            'footer_bg': '#f5f6fa',
            'main_bg': '#ecf0f1',
            'button_bg': '#d4a017',  # Dorado base
            'button_active': '#b8860b',  # Dorado oscuro
            'button_highlight': '#ffd700',  # Dorado claro
            'exit_button': '#e74c3c',
            'text_fg': '#2c3e50',
            'footer_fg': '#95a5a6'
        }
    
    def configurar_nltk(self):
        try:
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            try:
                nltk.data.find('tokenizers/punkt/spanish.pickle')
            except LookupError:
                nltk.download('punkt', quiet=True)
                nltk.download('cess_esp', quiet=True)
            
            nltk.download('stopwords', quiet=True)
            self.analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            messagebox.showerror("Error", f"Error configurando NLTK: {str(e)}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors['main_bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        header_frame = tk.Frame(main_frame, bg=self.colors['header_bg'])
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(
            header_frame,
            text="ANALIZADOR DE TENDENCIAS EN REDES SOCIALES",
            font=("Montserrat", 16, "bold"),
            bg=self.colors['header_bg'],
            fg="white",
            pady=15
        )
        header_label.pack()
        
        # Contenido principal
        content_frame = tk.Frame(main_frame, bg=self.colors['main_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sección de carga de archivo
        file_frame = tk.Frame(content_frame, bg=self.colors['main_bg'])
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            file_frame, 
            text="Base de Conocimiento (.pkl):",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        
        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.create_button(file_frame, "Examinar", self.browse_file)
        self.create_button(file_frame, "Cargar", self.load_knowledge_base)
        
        # Panel de información
        self.info_frame = tk.LabelFrame(
            content_frame, 
            text="Información de la Base de Conocimiento",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 10, "bold")
        )
        self.info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.topic_label = tk.Label(
            self.info_frame, 
            text="Tema: No cargado",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 9)
        )
        self.topic_label.pack(anchor=tk.W)
        
        self.hashtags_label = tk.Label(
            self.info_frame, 
            text="Hashtags relevantes: -",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 9)
        )
        self.hashtags_label.pack(anchor=tk.W)
        
        self.keywords_label = tk.Label(
            self.info_frame, 
            text="Palabras clave: -",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 9)
        )
        self.keywords_label.pack(anchor=tk.W)
        
        # Botón para generar ideas
        self.gen_ideas_btn = self.create_button(
            content_frame, 
            "Generar Ideas de Tendencias", 
            self.generate_ideas_threaded,
            state=tk.DISABLED,
            pady=(0, 20)
        )
        
        # Área de ideas generadas
        self.ideas_frame = tk.LabelFrame(
            content_frame, 
            text="Ideas Generadas",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 10, "bold")
        )
        self.ideas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ideas_text = scrolledtext.ScrolledText(
            self.ideas_frame, 
            height=8, 
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="white",
            fg=self.colors['text_fg']
        )
        self.ideas_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sección de análisis
        analysis_frame = tk.LabelFrame(
            content_frame, 
            text="Analizar Idea Propia",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 10, "bold")
        )
        analysis_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            analysis_frame, 
            text="Ingresa tu idea para analizar:",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W)
        
        self.idea_entry = ttk.Entry(analysis_frame)
        self.idea_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.idea_entry.bind("<Return>", lambda e: self.analyze_idea())
        
        self.create_button(
            analysis_frame, 
            "Analizar Idea", 
            self.analyze_idea,
            pady=(0, 5))
        
        # Área de resultados del análisis
        self.results_frame = tk.LabelFrame(
            content_frame, 
            text="Resultados del Análisis",
            bg=self.colors['main_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 10, "bold")
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="white",
            fg=self.colors['text_fg']
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.configure(state=tk.DISABLED)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        
        status_bar = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN,
            bg=self.colors['footer_bg'],
            fg=self.colors['text_fg'],
            font=("Segoe UI", 8),
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg=self.colors['footer_bg'])
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 0))  # <- Eliminado before=status_bar
        footer_frame.config(highlightbackground="red", highlightthickness=2)
        
        footer_label = tk.Label(
            footer_frame,
            text="© 2025 Analizador de Tendencias | Díaz Segovia D.",
            font=("Montserrat", 8),
            fg=self.colors['footer_fg'],
            bg=self.colors['footer_bg'],
            pady=5
        )
        footer_label.pack()
        
    
    def create_button(self, parent, text, command, state=tk.NORMAL, pady=0):
        btn_frame = tk.Frame(parent, bg=self.colors['main_bg'])
        btn_frame.pack(pady=pady)
        
        button = tk.Button(
            btn_frame, 
            text=text, 
            command=command,
            bg=self.colors['button_bg'],
            fg="white",
            font=("Montserrat", 10, "bold"),
            width=25,
            height=1,
            bd=0,
            activebackground=self.colors['button_active'],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            state=state
        )
        button.pack(fill=tk.X)
        
        # Efecto hover
        button.bind("<Enter>", lambda e: button.config(bg=self.colors['button_highlight']))
        button.bind("<Leave>", lambda e: button.config(bg=self.colors['button_bg']))
        
        return button
    
    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Archivos PKL", "*.pkl")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
    
    def load_knowledge_base(self):
        filename = self.file_entry.get()
        if not filename:
            messagebox.showerror("Error", "Por favor selecciona un archivo")
            return
        
        self.set_status("Cargando base de conocimiento...")
        self.gen_ideas_btn.config(state=tk.DISABLED)
        
        try:
            with open(filename, 'rb') as f:
                self.base_conocimiento = pickle.load(f)
            
            self.topic_label.config(text=f"Tema: {self.base_conocimiento['tema'].upper()}")
            
            hashtags = ', '.join([h[0] for h in self.base_conocimiento['hashtags'][:5]])
            self.hashtags_label.config(text=f"Hashtags relevantes: {hashtags}...")
            
            keywords = ', '.join([w[0] for w in self.base_conocimiento['palabras_positivas'][:3] + 
                                self.base_conocimiento['palabras_negativas'][:3]])
            self.keywords_label.config(text=f"Palabras clave: {keywords}...")
            
            self.gen_ideas_btn.config(state=tk.NORMAL)
            self.set_status("Base de conocimiento cargada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la base de conocimiento: {e}")
            self.set_status("Error al cargar el archivo")
    
    def generate_ideas_threaded(self):
        if self.loading:
            return
        
        self.loading = True
        self.set_status("Generando ideas...")
        self.gen_ideas_btn.config(state=tk.DISABLED)
        
        threading.Thread(target=self.generate_ideas, daemon=True).start()
    
    def generate_ideas(self):
        try:
            plantillas_ideas = [
                "El impacto de {concepto} en {contexto}",
                "Cómo {concepto} está cambiando {contexto}",
                "La relación entre {concepto} y {contexto}",
                "Tendencias emergentes en {concepto} para {contexto}",
                "Por qué {concepto} es importante para {contexto}",
                "El futuro de {concepto} en el ámbito de {contexto}",
                "{concepto}: una nueva perspectiva sobre {contexto}",
                "Desafíos y oportunidades de {concepto} en {contexto}"
            ]
            
            contextos = [
                "la sociedad actual", "las redes sociales", "la política moderna",
                "la economía digital", "la cultura juvenil", "la tecnología emergente",
                "las discusiones públicas", "el ámbito empresarial", "la educación",
                "las relaciones internacionales", "el medio ambiente"
            ]
            
            # Extraer componentes clave
            hashtags = [h[0].strip('#') for h in self.base_conocimiento['hashtags'] if not any(c.isdigit() for c in h[0])]
            palabras_clave = [w[0] for w in self.base_conocimiento['palabras_positivas'][:7]] + [w[0] for w in self.base_conocimiento['palabras_negativas'][:7]]
            
            # Filtrar elementos
            palabras_clave = [p for p in palabras_clave if len(p) > 3 and p.isalpha()]
            hashtags = [h for h in hashtags if len(h) > 3 and h.isalpha()]
            
            # Agrupar palabras por categorías
            categorias = defaultdict(list)
            for palabra in palabras_clave:
                if palabra.endswith(('ción', 'sión', 'miento', 'anza')):
                    categorias['conceptos'].append(palabra)
                elif palabra.endswith(('ar', 'er', 'ir')):
                    categorias['acciones'].append(palabra)
                else:
                    categorias['sustantivos'].append(palabra)
            
            # Generar ideas
            ideas_generadas = set()
            for _ in range(8):
                try:
                    plantilla = random.choice(plantillas_ideas)
                    contexto = random.choice(contextos)
                    
                    if "{concepto}" in plantilla:
                        if random.random() > 0.5 and categorias['conceptos']:
                            concepto = random.choice(categorias['conceptos'])
                        elif hashtags:
                            concepto = random.choice(hashtags)
                        else:
                            concepto = random.choice(palabras_clave)
                        
                        concepto = concepto.capitalize()
                        idea = plantilla.format(concepto=concepto, contexto=contexto)
                        ideas_generadas.add(idea)
                except:
                    continue
            
            # Completar si no hay suficientes ideas
            while len(ideas_generadas) < 5 and palabras_clave and hashtags:
                p1 = random.choice(palabras_clave)
                p2 = random.choice(hashtags)
                ideas_generadas.add(f"¿Cómo afectará {p1} a {p2} en el futuro cercano?")
            
            # Mostrar en el área de texto
            self.ideas_text.config(state=tk.NORMAL)
            self.ideas_text.delete(1.0, tk.END)
            self.ideas_text.insert(tk.END, "💡 POSIBLES TENDENCIAS Y TEMAS DE DISCUSIÓN:\n\n")
            
            for i, idea in enumerate(sorted(ideas_generadas, key=lambda x: len(x)), 1):
                self.ideas_text.insert(tk.END, f"{i}. {idea}\n\n")
            
            self.ideas_text.config(state=tk.DISABLED)
            self.set_status("Ideas generadas correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar ideas: {str(e)}")
            self.set_status("Error al generar ideas")
        
        finally:
            self.loading = False
            self.gen_ideas_btn.config(state=tk.NORMAL)
    
    def analyze_idea(self):
        idea = self.idea_entry.get().strip()
        if not idea:
            messagebox.showwarning("Advertencia", "Por favor ingresa una idea para analizar")
            return
        
        if len(idea.split()) < 3:
            messagebox.showwarning("Advertencia", "Por favor ingresa una idea más elaborada (mínimo 3 palabras)")
            return
        
        if not self.base_conocimiento:
            messagebox.showerror("Error", "Primero carga una base de conocimiento")
            return
        
        self.set_status(f"Analizando idea: {idea[:30]}...")
        
        try:
            idea_lower = idea.lower()
            
            # Componentes de análisis
            hashtags = [h[0].lower() for h in self.base_conocimiento['hashtags']]
            palabras_clave = [w[0].lower() for w in self.base_conocimiento['palabras_positivas'] + 
                            self.base_conocimiento['palabras_negativas']]
            
            # 1. Análisis de relevancia
            palabras_idea = set(nltk.word_tokenize(idea_lower, language='spanish'))
            palabras_idea.difference_update(set(nltk.corpus.stopwords.words('spanish')))
            
            matches_hashtags = sum(1 for h in hashtags if any(SequenceMatcher(None, h, p).ratio() > 0.7 for p in palabras_idea))
            matches_palabras = sum(1 for p in palabras_idea if p in palabras_clave)
            
            relevancia = (
                0.6 * min(matches_palabras / 5, 1.0) + 
                0.4 * min(matches_hashtags / 3, 1.0)
            )
            
            # 2. Análisis de sentimiento
            sentimiento = self.analyzer.polarity_scores(idea)['compound']
            
            # 3. Análisis de novedad
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
            
            # Mostrar resultados
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            
            self.results_text.insert(tk.END, "🔍 ANÁLISIS COMPLETO DE LA IDEA\n\n")
            self.results_text.insert(tk.END, f"📌 Tema analizado: '{idea.capitalize()}'\n\n")
            
            self.results_text.insert(tk.END, "📊 RESULTADOS:\n")
            self.results_text.insert(tk.END, f"- Puntuación de tendencia: {puntuacion:.2f}/100\n")
            self.results_text.insert(tk.END, f"- Relevancia histórica: {relevancia*100:.2f}%\n")
            self.results_text.insert(tk.END, f"- Novedad: {novedad*100:.2f}%\n")
            self.results_text.insert(tk.END, f"- Sentimiento público: {recepcion} ({sentimiento:.2f})\n\n")
            
            self.results_text.insert(tk.END, "💡 RECOMENDACIÓN:\n")
            self.results_text.insert(tk.END, f"{recomendacion}\n\n")
            
            # Sugerencias de mejora
            self.results_text.insert(tk.END, "🔧 SUGERENCIAS:\n")
            if matches_palabras < 2:
                self.results_text.insert(tk.END, "- Considera incluir más palabras clave relevantes\n")
            if matches_hashtags == 0:
                self.results_text.insert(tk.END, "- Relaciona con hashtags populares del tema\n")
            if novedad < 0.3:
                self.results_text.insert(tk.END, "- Añade elementos innovadores o de actualidad\n")
            
            self.results_text.config(state=tk.DISABLED)
            self.set_status(f"Análisis completado - Puntuación: {puntuacion:.2f}/100")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar la idea: {str(e)}")
            self.set_status("Error en el análisis")
    
    def set_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrendAnalyzerApp(root)
    root.mainloop()