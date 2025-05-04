import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont 
import asyncio
from twscrape import API
import pandas as pd
from pathlib import Path
from datetime import datetime
import threading

class TwitterScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scraper de Twitter - Configuración")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Variables para los campos de entrada
        self.tema_var = tk.StringVar()
        self.anio_var = tk.StringVar()
        self.idioma_var = tk.StringVar()
        self.limite_var = tk.IntVar()
        self.subcarpeta_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Esperando configuración...")
        
        # Configuración de estilo
        self.setup_style()
        
        # Frame principal
        self.main_frame = tk.Frame(root, bg="#f5f6fa")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        self.create_title_frame()
        
        # Formulario de configuración
        self.create_form_frame()
        
        # Área de estado y progreso
        self.create_status_frame()
        
        # Botones de acción
        self.create_action_buttons()
        
        # Footer
        self.create_footer()
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar fuentes
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=9)
        
        # Estilo para los botones
        style.configure('Aqua.TButton', 
                      font=('Segoe UI', 10, 'bold'), 
                      padding=10,
                      foreground='white',
                      background='#008080',  # Azul aqua
                      bordercolor='#008080',
                      relief='raised',
                      anchor='center')
        style.map('Aqua.TButton',
                background=[('active', '#20B2AA'), ('pressed', '#008B8B')],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure('Gold.TButton', 
                       font=('Segoe UI', 10, 'bold'), 
                       padding=10,
                       foreground='black',
                       background='#FFD700',  # Dorado
                       bordercolor='#DAA520',
                       relief='raised',
                       anchor='center')
        style.map('Gold.TButton',
                background=[('active', '#FFC125'), ('pressed', '#DAA520')],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        style.configure("Green.Horizontal.TProgressbar",
                   background='#76D7C4',  
                   troughcolor='#E8F8F5',  
                   bordercolor='#48C9B0',  
                   lightcolor='#A2D9CE',   
                   darkcolor='#45B39D')    
        
        # Estilo para los entry
        style.configure('TEntry', padding=5, relief='flat')
    
    def create_title_frame(self):
        title_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame, 
            text="CONFIGURACIÓN DE SCRAPER DE TWITTER", 
            font=("Segoe UI", 16, "bold"), 
            bg="#2c3e50", 
            fg="white",
            pady=15
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Complete los parámetros de búsqueda",
            font=("Segoe UI", 10),
            bg="#2c3e50",
            fg="#bdc3c7",
            pady=5
        )
        subtitle_label.pack()
    
    def create_form_frame(self):
        form_frame = tk.Frame(self.main_frame, bg="#ecf0f1", padx=20, pady=20)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Tema/Hashtag
        self.create_form_row(
            form_frame, 
            "Tema o hashtag:", 
            "Ej: #Python, IA, 'machine learning'", 
            self.tema_var,
            row=0
        )
        
        # Año
        self.create_form_row(
            form_frame, 
            "Año de búsqueda:", 
            f"Ej: {datetime.now().year}", 
            self.anio_var,
            row=1
        )
        
        # Idioma
        self.create_form_row(
            form_frame, 
            "Idioma (código):", 
            "es, en, fr, etc.", 
            self.idioma_var,
            row=2
        )
        
        # Límite de tweets
        self.create_form_row(
            form_frame, 
            "Límite de tweets:", 
            "", 
            self.limite_var,
            row=3,
            entry_class=ttk.Spinbox,
            entry_kwargs={"from_": 1, "to": 10000, "increment": 10}
        )
        
        # Subcarpeta
        self.create_form_row(
            form_frame, 
            "Subcarpeta (opcional):", 
            "Dejar vacío para guardar en DB/", 
            self.subcarpeta_var,
            row=4
        )
        
        # Botón para examinar subcarpetas existentes
        browse_btn = ttk.Button(
            form_frame,
            text="🔍 Examinar subcarpetas",
            command=self.browse_subfolders,
            style='Aqua.TButton'
        )
        browse_btn.grid(row=5, column=1, pady=10, sticky='w')
    
    def create_form_row(self, parent, label_text, placeholder, variable, row, 
                   entry_class=ttk.Entry, entry_kwargs=None):
        if entry_kwargs is None:
            entry_kwargs = {}
            
        label = tk.Label(
            parent,
            text=label_text,
            font=("Segoe UI", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            anchor='w'
        )
        label.grid(row=row, column=0, padx=10, pady=5, sticky='w')
        
        # Manejo especial para Spinbox
        if entry_class == ttk.Spinbox:
            entry = entry_class(
                parent,
                textvariable=variable,
                font=("Segoe UI", 10),
                **entry_kwargs
            )
            entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
            
            # Añadir placeholder manualmente
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e, w=entry, p=placeholder: w.delete(0, tk.END) if w.get() == p else None)
            entry.bind("<FocusOut>", lambda e, w=entry, p=placeholder: w.insert(0, p) if not w.get() else None)
            
            # Configurar validación para asegurar que solo se ingresen números
            def validate_spinbox(new_val):
                if new_val == "":
                    return True
                try:
                    int(new_val)
                    return True
                except ValueError:
                    return False
                    
            vcmd = (parent.register(validate_spinbox), '%P')
            entry.configure(validate='key', validatecommand=vcmd)
        else:
            # Comportamiento normal para otros widgets Entry
            entry = entry_class(
                parent,
                textvariable=variable,
                font=("Segoe UI", 10),
                **entry_kwargs
            )
            entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
            
            if isinstance(entry, ttk.Entry):
                entry.insert(0, placeholder)
                entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == placeholder else None)
                entry.bind("<FocusOut>", lambda e: entry.insert(0, placeholder) if not entry.get() else None)
        
        parent.grid_columnconfigure(1, weight=1)
    
    def browse_subfolders(self):
        initial_dir = Path("DB")
        if not initial_dir.exists():
            initial_dir.mkdir()
        
        folder = filedialog.askdirectory(
            title="Seleccionar subcarpeta",
            initialdir=str(initial_dir)
        )
        
        if folder:
            folder_path = Path(folder)
            if folder_path.parent.name == "DB":
                self.subcarpeta_var.set(folder_path.name)
            else:
                messagebox.showwarning(
                    "Ubicación incorrecta",
                    "Por favor seleccione una subcarpeta dentro de la carpeta DB")
    
    def create_status_frame(self):
        status_frame = tk.Frame(self.main_frame, bg="#ecf0f1", padx=20, pady=20)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            status_frame,
            orient='horizontal',
            mode='determinate',
            length=600,
            style='Green.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Etiqueta de estado
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            anchor='w'
        )
        status_label.pack(fill=tk.X)
    
    def create_action_buttons(self):
        button_frame = tk.Frame(self.main_frame, bg="#f5f6fa")
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Usar caracteres Unicode como iconos (o puedes cargar imágenes reales)
        start_icon = "▶"  # Triángulo de play
        cancel_icon = "✖"  # Equis
        
        # Botón de inicio con estilo aqua
        start_btn = ttk.Button(
            button_frame,
            text=f"  {start_icon} Iniciar Scraping",
            command=self.start_scraping,
            style='Aqua.TButton'
        )
        start_btn.pack(side=tk.LEFT, padx=20, ipadx=10, ipady=5)
        
        # Espaciador entre botones
        tk.Label(button_frame, bg="#f5f6fa", width=5).pack(side=tk.LEFT)
        
        # Botón de cancelar con estilo dorado
        cancel_btn = ttk.Button(
            button_frame,
            text=f"  {cancel_icon} Cancelar",
            command=self.cancel_scraping,
            style='Gold.TButton'
        )
        cancel_btn.pack(side=tk.RIGHT, padx=20, ipadx=10, ipady=5)
    
    def create_footer(self):
        footer = tk.Label(
            self.main_frame,
            text="© 2025 Twitter Scraper | Díaz Segovia D.",
            font=("Segoe UI", 8),
            fg="#95a5a6",
            bg="#f5f6fa"
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
    def validate_inputs(self):
        if not self.tema_var.get():
            messagebox.showerror("Error", "Debe especificar un tema o hashtag")
            return False
        
        if not self.anio_var.get().isdigit() or len(self.anio_var.get()) != 4:
            messagebox.showerror("Error", "El año debe ser un valor de 4 dígitos")
            return False
        
        if len(self.idioma_var.get()) != 2 or not self.idioma_var.get().isalpha():
            messagebox.showerror("Error", "El idioma debe ser un código de 2 letras")
            return False
        
        if self.limite_var.get() < 1:
            messagebox.showerror("Error", "El límite debe ser mayor a 0")
            return False
            
        return True
    
    def start_scraping(self):
        if not self.validate_inputs():
            return
            
        self.status_var.set("Preparando scraping...")
        self.progress["value"] = 0
        
        # Ejecutar en un hilo separado para no bloquear la interfaz
        threading.Thread(
            target=self.run_async_scraping,
            daemon=True
        ).start()
    
    def run_async_scraping(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.scrape_and_save_tweets())
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error durante el scraping: {str(e)}"))
        finally:
            loop.close()
    
    async def scrape_and_save_tweets(self):
        # Actualizar estado
        self.root.after(0, lambda: self.status_var.set("Iniciando scraping..."))
        
        # Configurar API
        api = API()
        
        # Configurar cuenta (esto debería moverse a configuración)
        await api.pool.add_account(
            username="TestT27133",
            password="AUDI_VID3",
            email="testeoprofundo@gmail.com",
            email_password="TestTe00",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Obtener parámetros de la interfaz
        tema = self.tema_var.get()
        año = self.anio_var.get()
        idioma = self.idioma_var.get()
        limite = self.limite_var.get()
        subcarpeta = self.subcarpeta_var.get()
        
        # Configurar rutas
        db_folder = Path("DB")
        db_folder.mkdir(exist_ok=True)
        
        if subcarpeta:
            subcarpeta_path = db_folder / subcarpeta
            subcarpeta_path.mkdir(exist_ok=True)
        else:
            subcarpeta_path = db_folder
        
        # Construir query
        query = f"{tema} lang:{idioma} since:{año}-01-01 until:{int(año)+1}-01-01"
        self.root.after(0, lambda: self.status_var.set(f"Buscando: {query}"))
        
        try:
            await api.pool.login_all()
            
            # Preparar nombre de archivo
            next_num = len(list(subcarpeta_path.glob("DB_*.xlsx"))) + 1
            filename = subcarpeta_path / f"DB_{next_num}_{tema[:20]}_{año}.xlsx"
            
            # Scrapear tweets
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
                
                # Actualizar progreso
                progress = (len(tweets) / limite) * 100
                def update_progress():
                    self.progress["value"] = progress
                self.root.after(0, update_progress)
                self.root.after(0, lambda: self.status_var.set(f"Obtenidos {len(tweets)} de {limite} tweets..."))
                
                if len(tweets) >= limite:
                    break
            
            if tweets:
                df = pd.DataFrame(tweets)
                df.to_excel(filename, index=False)
                
                self.root.after(0, lambda: self.status_var.set(
                    f"✅ {len(tweets)} tweets guardados en:\n{filename}"))
                def set_progress_to_100():
                    self.progress["value"] = 100
                self.root.after(0, set_progress_to_100)
                
                # Mostrar vista previa
                preview = df.head(3)[['Fecha', 'Usuario', 'Texto']].to_string(index=False)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Scraping completado", 
                    f"Se guardaron {len(tweets)} tweets.\n\nVista previa:\n\n{preview}"))
                
                # Cerrar la ventana después de 5 segundos
                self.root.after(5000, self.root.destroy)
            else:
                self.root.after(0, lambda: self.status_var.set("⚠️ No se encontraron tweets con esos parámetros"))
                self.root.after(0, lambda: messagebox.showwarning(
                    "Sin resultados", 
                    "No se encontraron tweets con los parámetros especificados"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error durante el scraping: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"❌ Error: {str(e)}"))
    
    def cancel_scraping(self):
        if messagebox.askyesno(
            "Confirmar cancelación", 
            "¿Está seguro que desea cancelar el proceso de scraping?",
            icon="question",
            default="no"
        ):
            self.status_var.set("Scraping cancelado por el usuario")
            self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    
    # Centrar la ventana
    window_width = 800
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    app = TwitterScraperApp(root)
    root.mainloop()