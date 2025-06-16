# ventana_gestion.py - Ventanas para gestión de recursos
import tkinter as tk
from tkinter import ttk, messagebox

# Implementación completa para VentanaGestionHangares
class VentanaGestionHangares(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gestión de Hangares")
        self.geometry("1000x500")
        self.configure(bg='#ecf0f1')
        self.crear_interfaz()
        self.actualizar_lista()
    
    def crear_interfaz(self):
        columns = ("ID", "Nombre", "Ubicación", "Capacidad", "Ocupación")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y')
    
    def actualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        hangares = self.parent.db.obtener_hangares()
        for h in hangares:
            self.tree.insert('', 'end', values=(h[0], h[1], h[2], h[3], f"{h[4]}/{h[3]}"))

class VentanaGestionTecnicos(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gestión de Técnicos")
        self.geometry("1000x500")  # Aumentado para mejor visualización
        self.configure(bg='#ecf0f1')
        self.crear_interfaz()
        self.actualizar_lista()  # Faltaba llamar a actualizar lista
    
    def crear_interfaz(self):
        # Columnas corregidas para técnicos
        columns = ("ID", "Nombre", "Especialidad", "Licencia", "Estado")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        # Configurar anchos de columnas
        self.tree.column("ID", width=50, anchor='center')
        self.tree.column("Nombre", width=200)
        self.tree.column("Especialidad", width=150)
        self.tree.column("Licencia", width=100, anchor='center')
        self.tree.column("Estado", width=80, anchor='center')
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y')
        
        # Botones adicionales
        btn_frame = tk.Frame(self, bg='#ecf0f1')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Actualizar", command=self.actualizar_lista,
                 bg='#3498db', fg='white').pack(side='left', padx=5)
    
    def actualizar_lista(self):
        # Limpiar datos antiguos
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener técnicos de la base de datos
        tecnicos = self.parent.db.obtener_tecnicos()
        
        # Insertar datos formateados
        for t in tecnicos:
            estado = "Activo" if t[4] else "Inactivo"
            self.tree.insert('', 'end', values=(
                t[0], 
                t[1], 
                t[2], 
                t[3], 
                estado
            ))
class VentanaInventarioPiezas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gestión de Inventario de Piezas")
        self.geometry("1000x500")
        self.configure(bg='#ecf0f1')
        self.crear_interfaz()
        self.actualizar_inventario()
    
    def crear_interfaz(self):
        columns = ("ID", "Nombre", "Descripción", "Stock", "Precio", "Proveedor", "Última Actualización")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y')
    
    def actualizar_inventario(self):
        piezas = self.parent.db.obtener_piezas()
        for p in piezas:
            self.tree.insert('', 'end', values=(
                p[0], p[1], p[2], p[3], f"Bs {p[4]:.2f}", p[5], p[6]
            ))