# ventana_mantenimiento.py - Ventanas para gestión de mantenimientos
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class VentanaProgramarMantenimiento(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Programar Mantenimiento")
        self.geometry("800x600")
        self.configure(bg='#ecf0f1')
        
        self.var_aeronave = tk.StringVar()
        self.var_tipo = tk.StringVar()
        self.var_fecha = tk.StringVar()
        self.var_tecnico = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_costo = tk.DoubleVar(value=0.0)
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        tk.Label(self, text="Programar Mantenimiento", font=('Arial', 18, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=20)
        
        main_frame = tk.Frame(self, bg='#ecf0f1')
        main_frame.pack(padx=40, pady=10, fill='both', expand=True)
        
        # Selección de aeronave
        tk.Label(main_frame, text="Aeronave:", bg='#ecf0f1').grid(row=0, column=0, sticky='w', pady=5)
        aeronaves = [f"{a[0]}|{a[1]} - {a[2]}" for a in self.parent.db.obtener_aeronaves()]
        ttk.Combobox(main_frame, textvariable=self.var_aeronave, values=aeronaves, width=40).grid(row=0, column=1, pady=5)
        # Tipo de mantenimiento
        tk.Label(main_frame, text="Tipo:", bg='#ecf0f1').grid(row=1, column=0, sticky='w', pady=5)
        ttk.Combobox(main_frame, textvariable=self.var_tipo, 
                    values=["Preventivo", "Correctivo", "Modificación"], width=40).grid(row=1, column=1, pady=5)
        
        # Fecha programada
        tk.Label(main_frame, text="Fecha Programada:", bg='#ecf0f1').grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(main_frame, textvariable=self.var_fecha, width=43).grid(row=2, column=1, pady=5)
        tk.Button(main_frame, text="Seleccionar Fecha", command=self.seleccionar_fecha).grid(row=2, column=2, padx=5)
        
        # Técnico responsable
        tk.Label(main_frame, text="Técnico:", bg='#ecf0f1').grid(row=3, column=0, sticky='w', pady=5)
    
        tecnicos = [f"{t[0]}|{t[1]} - {t[2]}" for t in self.parent.db.obtener_tecnicos()]
        ttk.Combobox(main_frame, textvariable=self.var_tecnico, values=tecnicos, width=40).grid(row=3, column=1, pady=5)
        # Descripción y costo
        tk.Label(main_frame, text="Descripción:", bg='#ecf0f1').grid(row=4, column=0, sticky='w', pady=5)
        ttk.Entry(main_frame, textvariable=self.var_descripcion, width=43).grid(row=4, column=1, pady=5)
        
        tk.Label(main_frame, text="Costo Estimado (Bs):", bg='#ecf0f1').grid(row=5, column=0, sticky='w', pady=5)
        ttk.Entry(main_frame, textvariable=self.var_costo, width=43).grid(row=5, column=1, pady=5)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='#ecf0f1')
        btn_frame.grid(row=6, column=0, columnspan=3, pady=20)
        tk.Button(btn_frame, text="Guardar", command=self.guardar_mantenimiento, 
                 bg='#2ecc71', fg='white', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy, 
                 bg='#e74c3c', fg='white', width=15).pack(side='right', padx=10)
        tk.Button(main_frame, text="Análisis Predictivo", 
                 command=self.analisis_predictivo,
                 bg='#9b59b6', fg='white').grid(row=0, column=2, padx=5)
    def analisis_predictivo(self):
        """Realizar análisis predictivo para la aeronave seleccionada"""
        if not self.var_aeronave.get():
            messagebox.showwarning("Advertencia", "Selecciona una aeronave primero")
            return
            
        try:
            # Obtener ID de aeronave
            aeronave_data = self.var_aeronave.get().split("|")[0]
            aeronave_id = int(aeronave_data)
            
            # Realizar análisis predictivo
            analisis = self.parent.ia_sistema.analizar_mantenimiento_predictivo(aeronave_id)
            
            if analisis:
                message = (
                    f"🔧 Análisis Predictivo 🔧\n\n"
                    f"🚨 Urgencia: {analisis['urgencia']}\n"
                    f"⏱️ Horas restantes: {analisis['horas_restantes']:.1f} h\n"
                    f"💰 Costo estimado: Bs {analisis['costo_estimado']:,.2f}\n\n"
                    f"📋 Recomendaciones:\n- " + "\n- ".join(analisis['recomendaciones'])
                )
                messagebox.showinfo("Análisis Predictivo", message)
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis predictivo: {str(e)}")
    
    def seleccionar_fecha(self):
        from tkcalendar import DateEntry
        top = tk.Toplevel(self)
        cal = DateEntry(top, date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        tk.Button(top, text="Seleccionar", command=lambda: self.actualizar_fecha(cal.get_date(), top)).pack()
    
    def actualizar_fecha(self, fecha, top):
        self.var_fecha.set(fecha.strftime("%Y-%m-%d"))
        top.destroy()
    
    def guardar_mantenimiento(self):
        # Validaciones
        if not all([self.var_aeronave.get(), self.var_tipo.get(), 
                   self.var_fecha.get(), self.var_tecnico.get()]):
            messagebox.showerror("Error", "Todos los campos obligatorios deben estar completos")
            return

        try:
            # Obtener ID de aeronave (formato: "ID|Matrícula - Modelo")
            aeronave_data = self.var_aeronave.get().split("|")[0]
            aeronave_id = int(aeronave_data)
            
            # Obtener ID de técnico (formato: "ID|Nombre - Especialidad")
            tecnico_data = self.var_tecnico.get().split("|")[0]
            tecnico_id = int(tecnico_data)
            
            costo = float(self.var_costo.get())
            
            if costo < 0:
                raise ValueError("Costo negativo")

        except (ValueError, IndexError, AttributeError) as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
            return

        # Insertar en la base de datos
        try:
            self.parent.db.insertar_mantenimiento(
                aeronave_id=aeronave_id,
                tipo=self.var_tipo.get(),
                fecha_programada=self.var_fecha.get(),
                tecnico_id=tecnico_id,
                descripcion=self.var_descripcion.get(),
                costo=costo
            )
            messagebox.showinfo("Éxito", "Mantenimiento registrado correctamente")
            self.destroy()
            
            # Actualizar lista si está abierta
            if hasattr(self.parent, 'ventana_historial'):
                self.parent.ventana_historial.actualizar_historial()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el mantenimiento: {str(e)}")

class VentanaAlertas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Alertas de Mantenimiento")
        self.geometry("800x400")
        self.configure(bg='#ecf0f1')
        
        self.crear_interfaz()
        self.actualizar_alertas()
    
    def crear_interfaz(self):
        tk.Label(self, text="Aeronaves con Mantenimiento Pendiente", 
                font=('Arial', 16, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        columns = ("Matrícula", "Modelo", "Horas Vuelo", "Categoría", "Horas Restantes")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y')
    
    def actualizar_alertas(self):
        aeronaves = self.parent.db.obtener_aeronaves_con_alertas()
        for a in aeronaves:
            self.tree.insert('', 'end', values=(
                a[1], a[2], f"{a[6]:.1f} h", a[5], 
                self.calcular_horas_restantes(a[5], a[6])
            ))
    
    def calcular_horas_restantes(self, categoria, horas_actuales):
        limites = {'Liviana': 100, 'Mediana': 150, 'Pesada': 200}
        return f"{limites[categoria] - horas_actuales:.1f} h"
def guardar_mantenimiento(self):
    # Validaciones
    if not all([self.var_aeronave.get(), self.var_tipo.get(), 
               self.var_fecha.get(), self.var_tecnico.get()]):
        messagebox.showerror("Error", "Campos obligatorios faltantes")
        return
    
    try:
        aeronave_id = int(self.var_aeronave.get().split(" - ")[0])
        tecnico_id = int(self.var_tecnico.get().split(" - ")[0])
        costo = float(self.var_costo.get())
    except (ValueError, IndexError):
        messagebox.showerror("Error", "Selección inválida")
        return
    
    # Insertar en BD
    success = self.parent.db.insertar_mantenimiento(
        aeronave_id=aeronave_id,
        tipo=self.var_tipo.get(),
        fecha_programada=self.var_fecha.get(),
        tecnico_id=tecnico_id,
        descripcion=self.var_descripcion.get(),
        costo=costo
    )
    
    if success:
        messagebox.showinfo("Éxito", "Mantenimiento programado")
        self.destroy()
class VentanaHistorialTecnico(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Historial Técnico")
        self.geometry("1200x600")
        self.configure(bg='#ecf0f1')
        self.crear_interfaz()
        self.actualizar_historial()

    def crear_interfaz(self):
        tk.Label(self, text="Historial de Mantenimientos Registrados", 
                font=('Arial', 16, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        columns = ("ID", "Aeronave", "Modelo", "Tipo", "Fecha Programada", 
                 "Técnico", "Estado", "Costo (Bs)")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y')

    def actualizar_historial(self):
        mantenimientos = self.parent.db.obtener_mantenimientos()
        for m in mantenimientos:
            self.tree.insert('', 'end', values=(
                m[0], m[7], m[8], m[2], m[3],
                m[9], m[6], f"{m[8]:,.2f}"
            ))