# ventana_reportes.py - Ventanas para reportes y estadísticas
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VentanaEstadisticas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Estadísticas Generales")
        self.geometry("1000x800")
        self.crear_interfaz()
    
    def crear_interfaz(self):
        stats = self.parent.db.obtener_estadisticas_generales()
        
        # Gráfico de categorías
        fig = plt.Figure(figsize=(6,4))
        ax = fig.add_subplot(111)
        categorias = list(stats['aeronaves_por_categoria'].keys())
        valores = list(stats['aeronaves_por_categoria'].values())
        ax.bar(categorias, valores)
        ax.set_title("Aeronaves por Categoría")
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

class VentanaReporteCostos(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Reporte de Costos")
        self.geometry("800x600")
        self.crear_interfaz()
    
    def crear_interfaz(self):
        stats = self.parent.db.obtener_estadisticas_generales()
        
        fig = plt.Figure(figsize=(8,5))
        ax = fig.add_subplot(111)
        
        # Gráfico de torta de costos por tipo
        costos = self.parent.db.obtener_costos_por_tipo()
        ax.pie(
            [c[1] for c in costos],
            labels=[c[0] for c in costos],
            autopct='%1.1f%%'
        )
        ax.set_title("Distribución de Costos por Tipo de Mantenimiento")
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack()
