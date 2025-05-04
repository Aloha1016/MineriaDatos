import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from tkinter import font as tkfont

class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Análisis de Datos")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configuración de estilo
        self.setup_style()
        
        # Frame principal con degradado
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título 
        title_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame, 
            text="SISTEMA DE ANÁLISIS DE DATOS", 
            font=("Montserrat", 18, "bold"), 
            bg="#2c3e50", 
            fg="white",
            pady=15
        )
        title_label.pack()
        
        # Frame para los botones
        button_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        button_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        # Subtítulo
        subtitle = tk.Label(
            button_frame,
            text="Seleccione una opción del menú",
            font=("Montserrat", 12),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        subtitle.pack(pady=(10, 20))
        
        # Botones principales
        self.create_button(button_frame, "Análisis de datos", "Analisis.py", "#3498db")
        self.create_button(button_frame, "Obtener datos", "RecopilacionDeTweets.py", "#2ba08b")
        self.create_button(button_frame, "Modelo de predicciones", "Predicciones.py", "#ff9800")
        
        # Botón de salida
        exit_button = tk.Button(
            self.main_frame, 
            text="Salir del sistema", 
            command=self.confirm_exit,
            bg="#e74c3c",
            fg="white",
            font=("Montserrat", 10, "bold"),
            width=20,
            height=2,
            bd=0,
            activebackground="#2c3e50",
            activeforeground="white"
        )
        exit_button.pack(pady=(0, 20))
        
        # Footer
        footer = tk.Label(
            self.main_frame,
            text="© 2025 Sistema de Análisis de Datos | Díaz Segovia D.",
            font=("Montserrat", 8),
            fg="#95a5a6",
            bg="#f5f6fa"
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
    def setup_style(self):
        # Estilo para los botones
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar fuentes 
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=9)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family="Segoe UI", size=9)
    
    def create_button(self, frame, text, script, color):
        btn_frame = tk.Frame(frame, bg="#ecf0f1")
        btn_frame.pack(pady=8, fill=tk.X, padx=40)
        
        button = tk.Button(
            btn_frame, 
            text=text, 
            command=lambda: self.ejecutar_script(script),
            bg=color,
            fg="white",
            font=("Montserrat", 11, "bold"),
            width=25,
            height=2,
            bd=0,
            activebackground=self.darken_color(color),
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2"
        )
        button.pack(fill=tk.X)
        
        # Efecto hover
        button.bind("<Enter>", lambda e: button.config(bg=self.lighten_color(color)))
        button.bind("<Leave>", lambda e: button.config(bg=color))
    
    def ejecutar_script(self, ruta_script):
        try:
            if not os.path.exists(ruta_script):
                messagebox.showerror("Error", f"Archivo no encontrado: {ruta_script}")
                return
                
            # Usamos el mismo intérprete de Python que está ejecutando este script
            subprocess.run([sys.executable, ruta_script], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al ejecutar {ruta_script}: {e}")
    
    def confirm_exit(self):
        if messagebox.askyesno(
            "Confirmar salida", 
            "¿Está seguro que desea salir del sistema?",
            icon="question",
            default="no"
        ):
            self.root.destroy()
    
    @staticmethod
    def darken_color(hex_color, factor=0.2):
        """Oscurece un color hexadecimal"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = [int(c * (1 - factor)) for c in rgb]
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'
    
    @staticmethod
    def lighten_color(hex_color, factor=0.2):
        """Aclara un color hexadecimal"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened = [min(255, int(c + (255 - c) * factor)) for c in rgb]
        return f'#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}'

if __name__ == "__main__":
    root = tk.Tk()
    
    # Centrar la ventana
    window_width = 600
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    app = MenuApp(root)
    root.mainloop()