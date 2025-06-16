import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager
from ventana_aeronaves import VentanaRegistroAeronave, VentanaListaAeronaves
from ventana_mantenimiento import VentanaProgramarMantenimiento, VentanaHistorialTecnico, VentanaAlertas
from ventana_gestion import VentanaGestionHangares, VentanaGestionTecnicos, VentanaInventarioPiezas
from ventana_reportes import VentanaEstadisticas, VentanaReporteCostos
from ia_aeronaves import VentanaIAAeronaves, SistemaIAAeronaves

class SGMA(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Mantenimiento de Aeronaves - Bolivia by lizbeth + IA")
        self.geometry('1000x800')
        self.configure(bg='#2c3e50')
        
        # Inicializar base de datos
        self.db = DatabaseManager()
        
        # Inicializar sistema de IA
        self.ia_sistema = SistemaIAAeronaves(self)
        
        # Crear interfaz
        self.crear_menu()
        self.crear_interfaz_principal()
        
    def crear_menu(self):
        """Crear barra de menú principal"""
        self.barra_menu = tk.Menu(self)
        
        # Menú Aeronaves
        menu_aeronaves = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label='Aeronaves', menu=menu_aeronaves)
        menu_aeronaves.add_command(label='Registrar Aeronave', command=self.abrir_registro_aeronave)
        menu_aeronaves.add_command(label='Lista de Aeronaves', command=self.abrir_lista_aeronaves)
        menu_aeronaves.add_separator()
        menu_aeronaves.add_command(label='Categorías por Peso', command=self.mostrar_categorias)
        
        # Menú Mantenimiento
        menu_mantenimiento = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label='Mantenimiento', menu=menu_mantenimiento)
        menu_mantenimiento.add_command(label='Programar Mantenimiento', command=self.abrir_programar_mantenimiento)
        menu_mantenimiento.add_command(label='Historial Técnico', command=self.abrir_historial_tecnico)
        menu_mantenimiento.add_command(label='Alertas de Revisión', command=self.abrir_alertas)
        
        # Menú Gestión
        menu_gestion = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label='Gestión', menu=menu_gestion)
        menu_gestion.add_command(label='Hangares', command=self.abrir_gestion_hangares)
        menu_gestion.add_command(label='Técnicos', command=self.abrir_gestion_tecnicos)
        menu_gestion.add_command(label='Inventario Piezas', command=self.abrir_inventario_piezas)
        
        # Menú Reportes
        menu_reportes = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label='Reportes', menu=menu_reportes)
        menu_reportes.add_command(label='Estadísticas Generales', command=self.abrir_estadisticas)
        menu_reportes.add_command(label='Reporte de Costos', command=self.abrir_reporte_costos)
        
        # Menú Inteligencia Artificial
        menu_ia = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label='Inteligencia Artificial', menu=menu_ia)
        menu_ia.add_command(label='Clasificación y Predicción', command=self.abrir_ia_aeronaves)
        menu_ia.add_command(label='Entrenar Modelo IA', command=self.entrenar_modelo_ia)
        
        self.config(menu=self.barra_menu)
        
    def crear_interfaz_principal(self):
        """Crear interfaz principal con dashboard"""
        # Frame principal
        main_frame = tk.Frame(self, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(main_frame, text="Sistema de Gestión de Mantenimiento de Aeronaves", 
                         font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50')
        titulo.pack(pady=(0, 30))
        
        # Subtitle
        subtitulo = tk.Label(main_frame, text="Autoridad de Aviación Civil - Bolivia", 
                           font=('Arial', 14), fg='#ecf0f1', bg='#2c3e50')
        subtitulo.pack(pady=(0, 40))
        
        # Dashboard con estadísticas
        dashboard_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        dashboard_frame.pack(fill='x', pady=20)
        
        tk.Label(dashboard_frame, text="Dashboard - Estado Actual", 
                font=('Arial', 16, 'bold'), fg='white', bg='#34495e').pack(pady=10)
        
        # Stats grid
        stats_frame = tk.Frame(dashboard_frame, bg='#34495e')
        stats_frame.pack(pady=20)
        
        # Obtener estadísticas de la base de datos
        total_aeronaves = len(self.db.obtener_aeronaves())
        mantenimientos_activos = len([m for m in self.db.obtener_mantenimientos() if m[6] == 'En Proceso'])
        total_tecnicos = len(self.db.obtener_tecnicos())
        total_hangares = len(self.db.obtener_hangares())
        
        self.crear_stat_box(stats_frame, "Aeronaves Registradas", str(total_aeronaves), "#3498db", 0, 0)
        self.crear_stat_box(stats_frame, "Mantenimientos Activos", str(mantenimientos_activos), "#e74c3c", 0, 1)
        self.crear_stat_box(stats_frame, "Técnicos Disponibles", str(total_tecnicos), "#2ecc71", 0, 2)
        self.crear_stat_box(stats_frame, "Hangares Operativos", str(total_hangares), "#f39c12", 0, 3)
        
        # Accesos rápidos
        accesos_frame = tk.Frame(main_frame, bg='#2c3e50')
        accesos_frame.pack(fill='x', pady=30)
        
        tk.Label(accesos_frame, text="Accesos Rápidos", 
                font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50').pack(pady=(0, 15))
        
        botones_frame = tk.Frame(accesos_frame, bg='#2c3e50')
        botones_frame.pack()
        
        tk.Button(botones_frame, text="Registrar Aeronave", command=self.abrir_registro_aeronave,
                 bg='#3498db', fg='white', font=('Arial', 12), width=18, height=2).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(botones_frame, text="Programar Mantenimiento", command=self.abrir_programar_mantenimiento,
                 bg='#e74c3c', fg='white', font=('Arial', 12), width=18, height=2).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(botones_frame, text="Ver Alertas", command=self.abrir_alertas,
                 bg='#f39c12', fg='white', font=('Arial', 12), width=18, height=2).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(botones_frame, text="Inteligencia Artificial", command=self.abrir_ia_aeronaves,
                 bg='#9b59b6', fg='white', font=('Arial', 12), width=18, height=2).grid(row=0, column=3, padx=10, pady=5)
    
    def crear_stat_box(self, parent, titulo, valor, color, row, col):
        """Crear una caja de estadística"""
        frame = tk.Frame(parent, bg=color, width=200, height=100)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        frame.grid_propagate(False)
        
        tk.Label(frame, text=valor, font=('Arial', 24, 'bold'), 
                fg='white', bg=color).pack(expand=True)
        tk.Label(frame, text=titulo, font=('Arial', 10), 
                fg='white', bg=color).pack()
    
    def categorizar_aeronave(self, peso_mtow):
        """Categorizar aeronave según su peso MTOW"""
        if peso_mtow <= 5700:
            return "Liviana"
        elif peso_mtow <= 27000:
            return "Mediana"
        else:
            return "Pesada"
    
    def mostrar_categorias(self):
        """Mostrar información sobre categorías de aeronaves"""
        info = """
        CATEGORÍAS DE AERONAVES POR PESO (MTOW - Maximum Take-Off Weight):
        
        • LIVIANA: Hasta 5,700 kg
          - Aviones pequeños, vuelos cortos
          - Mantenimiento cada 100 horas de vuelo
          
        • MEDIANA: 5,701 kg - 27,000 kg  
          - Aviones comerciales regionales
          - Mantenimiento cada 150 horas de vuelo
          
        • PESADA: Más de 27,000 kg
          - Aviones comerciales grandes
          - Mantenimiento cada 200 horas de vuelo
        """
        messagebox.showinfo("Categorías de Aeronaves", info)
    
    # Métodos para abrir ventanas
    def abrir_registro_aeronave(self):
        VentanaRegistroAeronave(self)
    
    def abrir_lista_aeronaves(self):
        VentanaListaAeronaves(self)
    
    def abrir_programar_mantenimiento(self):
        VentanaProgramarMantenimiento(self)
    
    def abrir_historial_tecnico(self):
        VentanaHistorialTecnico(self)
    
    def abrir_alertas(self):
        VentanaAlertas(self)
    
    def abrir_gestion_hangares(self):
        VentanaGestionHangares(self)
    
    def abrir_gestion_tecnicos(self):
        VentanaGestionTecnicos(self)
    
    def abrir_inventario_piezas(self):
        VentanaInventarioPiezas(self)
    
    def abrir_estadisticas(self):
        VentanaEstadisticas(self)
    
    def abrir_reporte_costos(self):
        VentanaReporteCostos(self)
    
    def abrir_ia_aeronaves(self):
        VentanaIAAeronaves(self)
    
    def entrenar_modelo_ia(self):
        """Entrenar el modelo de IA y mostrar resultados"""
        resultado = self.ia_sistema.entrenar_modelo()
        if resultado:
            messagebox.showinfo("Entrenamiento IA", "Modelo de IA entrenado exitosamente")
        else:
            messagebox.showerror("Entrenamiento IA", "Error al entrenar el modelo de IA")

if __name__ == "__main__":
    app = SGMA()
    app.mainloop()