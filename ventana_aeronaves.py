# ventana_aeronaves.py - Ventanas para gestión de aeronaves
import tkinter as tk
from tkinter import ttk, messagebox

class VentanaRegistroAeronave(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Registrar Aeronave")
        self.geometry("600x500")
        self.configure(bg='#ecf0f1')
        
        # Variables
        self.var_matricula = tk.StringVar()
        self.var_modelo = tk.StringVar()
        self.var_fabricante = tk.StringVar()
        self.var_peso_mtow = tk.StringVar()
        self.var_horas_vuelo = tk.StringVar()
        self.var_hangar = tk.StringVar()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Título
        tk.Label(self, text="Registro de Aeronave", font=('Arial', 18, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(self, bg='#ecf0f1')
        main_frame.pack(padx=40, pady=20, fill='both', expand=True)
        
        # Campos del formulario
        campos = [
            ("Matrícula (CP-XXXX):", self.var_matricula),
            ("Modelo:", self.var_modelo),
            ("Fabricante:", self.var_fabricante),
            ("Peso MTOW (kg):", self.var_peso_mtow),
            ("Horas de Vuelo:", self.var_horas_vuelo)
        ]
        
        for i, (label_text, var) in enumerate(campos):
            tk.Label(main_frame, text=label_text, font=('Arial', 12), 
                    bg='#ecf0f1', fg='#2c3e50').grid(row=i, column=0, sticky='w', pady=8)
            tk.Entry(main_frame, textvariable=var, font=('Arial', 12), 
                    width=25).grid(row=i, column=1, padx=20, pady=8)
        
        # Selección de hangar
        tk.Label(main_frame, text="Hangar:", font=('Arial', 12), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=len(campos), column=0, sticky='w', pady=8)
        
        hangares = self.parent.db.obtener_hangares()
        hangar_values = [f"{h[1]} - {h[2]}" for h in hangares]  # nombre - ubicación
        
        hangar_combo = ttk.Combobox(main_frame, textvariable=self.var_hangar, 
                                   values=hangar_values,
                                   font=('Arial', 12), width=23)
        hangar_combo.grid(row=len(campos), column=1, padx=20, pady=8)
        
        # Información de categorías
        info_frame = tk.Frame(main_frame, bg='#d5dbdb', relief='sunken', bd=2)
        info_frame.grid(row=len(campos)+1, column=0, columnspan=2, pady=20, padx=10, sticky='ew')
        
        info_text = """💡 CATEGORÍAS AUTOMÁTICAS POR PESO MTOW:
• Liviana: ≤ 5,700 kg (Mantenimiento cada 100h)
• Mediana: 5,701-27,000 kg (Mantenimiento cada 150h)  
• Pesada: > 27,000 kg (Mantenimiento cada 200h)"""
        
        tk.Label(info_frame, text=info_text, font=('Arial', 9), 
                bg='#d5dbdb', fg='#2c3e50', justify='left').pack(padx=10, pady=10)

        # Botones
        btn_frame = tk.Frame(main_frame, bg='#ecf0f1')
        btn_frame.grid(row=len(campos)+2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Guardar", command=self.guardar_aeronave,
                 bg='#2ecc71', fg='white', font=('Arial', 12), width=12).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 12), width=12).pack(side='right', padx=10)
        tk.Button(main_frame, text="Predecir con IA", 
                 command=self.predecir_con_ia, bg='#3498db', fg='white').grid(row=3, column=2, padx=5)
        self.lbl_sugerencia = tk.Label(main_frame, text="", bg='#ecf0f1', fg='#27ae60')
        self.lbl_sugerencia.grid(row=4, column=1, columnspan=2, sticky='w')

    def predecir_con_ia(self):
        """Usar IA para predecir categoría y sugerir fabricante"""
        try:
            peso = float(self.var_peso_mtow.get())
            # Predecir categoría usando IA
            categoria, confianza = self.parent.ia_sistema.predecir_categoria(peso, 0)
            
            # Sugerir fabricante
            fabricantes_sugeridos = self.parent.ia_sistema.sugerir_fabricante(peso, categoria)
            
            # Actualizar interfaz
            self.lbl_sugerencia.config(
                text=f"IA sugiere: Categoría {categoria} | Fabricantes: {', '.join(fabricantes_sugeridos[:3])}"
            )
            
            # Autocompletar fabricante si es posible
            if fabricantes_sugeridos:
                self.var_fabricante.set(fabricantes_sugeridos[0])
                
        except ValueError:
            messagebox.showerror("Error", "Ingrese un peso válido primero")
            
    def guardar_aeronave(self):
        """Validar y guardar la aeronave en la base de datos"""
        # Validaciones
        if not all([self.var_matricula.get(), self.var_modelo.get(), 
                   self.var_fabricante.get(), self.var_peso_mtow.get(),
                   self.var_horas_vuelo.get(), self.var_hangar.get()]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            peso_mtow = float(self.var_peso_mtow.get())
            horas_vuelo = float(self.var_horas_vuelo.get())
        except ValueError:
            messagebox.showerror("Error", "Peso y horas de vuelo deben ser números válidos")
            return
        
        # Obtener ID del hangar seleccionado
        hangar_seleccionado = self.var_hangar.get().split(" - ")[0]
        hangar = self.parent.db.obtener_hangar_por_nombre(hangar_seleccionado)
        
        if not hangar:
            messagebox.showerror("Error", "Hangar no válido")
            return
        
        # Insertar en la base de datos
        success = self.parent.db.insertar_aeronave(
            matricula=self.var_matricula.get(),
            modelo=self.var_modelo.get(),
            fabricante=self.var_fabricante.get(),
            peso_mtow=peso_mtow,
            categoria=self.parent.categorizar_aeronave(peso_mtow),
            horas_vuelo=horas_vuelo,
            hangar_id=hangar[0]
        )
        
        if success:
            messagebox.showinfo("Éxito", "Aeronave registrada correctamente")
            self.destroy()
            self.parent.abrir_lista_aeronaves()  # Actualizar lista
        else:
            messagebox.showerror("Error", "Matrícula ya existe en el sistema")

class VentanaListaAeronaves(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Lista de Aeronaves Registradas")
        self.geometry("1000x600")
        self.configure(bg='#ecf0f1')
        
        self.crear_interfaz()
        self.actualizar_lista()
    
    def crear_interfaz(self):
        # Título
        tk.Label(self, text="Aeronaves Registradas", font=('Arial', 18, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=20)
        
        # Treeview
        columns = ("ID", "Matrícula", "Modelo", "Fabricante", "Peso MTOW", "Categoría", "Horas Vuelo", "Hangar")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', selectmode='browse')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        self.tree.column("Modelo", width=150)
        self.tree.column("Hangar", width=150)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y')
    
    def actualizar_lista(self):
        # Limpiar datos antiguos
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener y cargar nuevos datos
        aeronaves = self.parent.db.obtener_aeronaves()
        for a in aeronaves:
            self.tree.insert('', 'end', values=(
                a[0], a[1], a[2], a[3], f"{a[4]:,.2f} kg", 
                a[5], f"{a[6]:,.1f} h", a[8]
            ))