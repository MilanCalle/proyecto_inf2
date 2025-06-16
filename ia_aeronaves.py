# ia_aeronaves.py - Sistema de IA para clasificación y predicción de aeronaves
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime

class SistemaIAAeronaves:
    def __init__(self, parent):
        self.parent = parent
        self.modelo = None
        self.scaler = StandardScaler()
        self.label_encoder_categoria = LabelEncoder()
        self.label_encoder_fabricante = LabelEncoder()
        self.fabricantes_conocidos = []
        self.modelo_entrenado = False
        
        # Crear directorio para modelos si no existe
        if not os.path.exists('modelos_ia'):
            os.makedirs('modelos_ia')
    
    def preparar_datos_entrenamiento(self):
        """Preparar datos de aeronaves existentes para entrenamiento"""
        aeronaves = self.parent.db.obtener_aeronaves()
        
        if len(aeronaves) < 10:
            # Si hay pocos datos, agregar datos sintéticos para entrenamiento
            datos_sinteticos = self.generar_datos_sinteticos()
            return datos_sinteticos
        
        # Preparar datos reales
        X = []
        y = []
        fabricantes = []
        
        for aeronave in aeronaves:
            # Características: peso_mtow, horas_vuelo, año_fabricacion_estimado
            peso_mtow = aeronave[4] if aeronave[4] else 10000
            horas_vuelo = aeronave[6] if aeronave[6] else 100
            
            # Estimar año de fabricación basado en horas de vuelo (aproximación)
            ano_estimado = 2024 - int(horas_vuelo / 500) if horas_vuelo > 500 else 2020
            
            X.append([peso_mtow, horas_vuelo, ano_estimado])
            y.append(aeronave[5])  # categoría
            fabricantes.append(aeronave[3])  # fabricante
        
        return np.array(X), np.array(y), np.array(fabricantes)
    
    def generar_datos_sinteticos(self):
        """Generar datos sintéticos para entrenamiento inicial"""
        np.random.seed(42)
        
        # Datos para aeronaves livianas
        livianas = []
        for _ in range(50):
            peso = np.random.uniform(500, 5700)
            horas = np.random.uniform(50, 1000)
            ano = np.random.randint(2010, 2024)
            livianas.append([peso, horas, ano, "Liviana", 
                           np.random.choice(["Cessna", "Piper", "Beechcraft"])])
        
        # Datos para aeronaves medianas
        medianas = []
        for _ in range(40):
            peso = np.random.uniform(5701, 27000)
            horas = np.random.uniform(200, 2000)
            ano = np.random.randint(2005, 2023)
            medianas.append([peso, horas, ano, "Mediana", 
                           np.random.choice(["Embraer", "Bombardier", "ATR"])])
        
        # Datos para aeronaves pesadas
        pesadas = []
        for _ in range(30):
            peso = np.random.uniform(27001, 400000)
            horas = np.random.uniform(500, 5000)
            ano = np.random.randint(2000, 2022)
            pesadas.append([peso, horas, ano, "Pesada", 
                          np.random.choice(["Boeing", "Airbus", "McDonnell Douglas"])])
        
        # Combinar todos los datos
        todos_datos = livianas + medianas + pesadas
        np.random.shuffle(todos_datos)
        
        X = np.array([[d[0], d[1], d[2]] for d in todos_datos])
        y = np.array([d[3] for d in todos_datos])
        fabricantes = np.array([d[4] for d in todos_datos])
        
        return X, y, fabricantes
    
    def entrenar_modelo(self):
        """Entrenar el modelo de clasificación"""
        try:
            # Obtener datos
            X, y, fabricantes = self.preparar_datos_entrenamiento()
            
            if len(X) == 0:
                messagebox.showerror("Error", "No hay datos suficientes para entrenar")
                return False
            
            # Normalizar características
            X_scaled = self.scaler.fit_transform(X)
            
            # Codificar etiquetas
            y_encoded = self.label_encoder_categoria.fit_transform(y)
            self.label_encoder_fabricante.fit(fabricantes)
            self.fabricantes_conocidos = list(self.label_encoder_fabricante.classes_)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Entrenar modelo
            self.modelo = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.modelo.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = self.modelo.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Guardar modelo
            self.guardar_modelo()
            self.modelo_entrenado = True
            
            messagebox.showinfo("Éxito", 
                              f"Modelo entrenado exitosamente!\n"
                              f"Precisión: {accuracy:.2%}\n"
                              f"Datos de entrenamiento: {len(X)} aeronaves")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al entrenar modelo: {str(e)}")
            return False
    
    def predecir_categoria(self, peso_mtow, horas_vuelo, ano_fabricacion=None):
        """Predecir categoría de aeronave usando IA"""
        if not self.modelo_entrenado:
            if not self.cargar_modelo():
                return None, 0.0
        
        try:
            # Preparar datos de entrada
            if ano_fabricacion is None:
                ano_fabricacion = 2020  # Valor por defecto
            
            X_input = np.array([[peso_mtow, horas_vuelo, ano_fabricacion]])
            X_input_scaled = self.scaler.transform(X_input)
            
            # Hacer predicción
            prediccion = self.modelo.predict(X_input_scaled)[0]
            probabilidades = self.modelo.predict_proba(X_input_scaled)[0]
            
            # Decodificar resultado
            categoria_predicha = self.label_encoder_categoria.inverse_transform([prediccion])[0]
            confianza = max(probabilidades)
            
            return categoria_predicha, confianza
            
        except Exception as e:
            print(f"Error en predicción: {e}")
            return None, 0.0
    
    def sugerir_fabricante(self, peso_mtow, categoria):
        """Sugerir fabricante basado en peso y categoría"""
        sugerencias = {
            "Liviana": {
                "peso_bajo": ["Cessna", "Piper", "Diamond"],
                "peso_alto": ["Beechcraft", "Mooney", "Cirrus"]
            },
            "Mediana": {
                "peso_bajo": ["Embraer", "ATR", "Bombardier"],
                "peso_alto": ["Saab", "Fokker", "BAe"]
            },
            "Pesada": {
                "peso_bajo": ["Boeing", "Airbus", "Embraer"],
                "peso_alto": ["Boeing", "Airbus", "McDonnell Douglas"]
            }
        }
        
        if categoria in sugerencias:
            if categoria == "Liviana":
                subcategoria = "peso_bajo" if peso_mtow < 3000 else "peso_alto"
            elif categoria == "Mediana":
                subcategoria = "peso_bajo" if peso_mtow < 15000 else "peso_alto"
            else:  # Pesada
                subcategoria = "peso_bajo" if peso_mtow < 100000 else "peso_alto"
            
            return sugerencias[categoria][subcategoria]
        
        return ["Boeing", "Airbus", "Cessna"]
    
    def analizar_mantenimiento_predictivo(self, aeronave_id):
        """Análisis predictivo para mantenimiento"""
        aeronave = self.parent.db.obtener_aeronave_por_id(aeronave_id)
        if not aeronave:
            return None
        
        peso_mtow = aeronave[4]
        horas_vuelo = aeronave[6]
        categoria = aeronave[5]
        
        # Algoritmo simple de predicción de mantenimiento
        limites_mantenimiento = {
            "Liviana": 100,
            "Mediana": 150,
            "Pesada": 200
        }
        
        limite = limites_mantenimiento.get(categoria, 150)
        horas_restantes = limite - (horas_vuelo % limite)
        
        # Calcular urgencia
        if horas_restantes <= 10:
            urgencia = "CRÍTICA"
            color = "#e74c3c"
        elif horas_restantes <= 25:
            urgencia = "ALTA"
            color = "#f39c12"
        elif horas_restantes <= 50:
            urgencia = "MEDIA"
            color = "#f1c40f"
        else:
            urgencia = "BAJA"
            color = "#2ecc71"
        
        # Predicción de costos (estimación basada en categoría y horas)
        costo_base = {
            "Liviana": 1500,
            "Mediana": 5000,
            "Pesada": 15000
        }
        
        factor_horas = 1 + (horas_vuelo / 10000)  # Mayor costo con más horas
        costo_estimado = costo_base.get(categoria, 5000) * factor_horas
        
        return {
            "horas_restantes": horas_restantes,
            "urgencia": urgencia,
            "color": color,
            "costo_estimado": costo_estimado,
            "recomendaciones": self.generar_recomendaciones(categoria, horas_vuelo)
        }
    
    def generar_recomendaciones(self, categoria, horas_vuelo):
        """Generar recomendaciones de mantenimiento"""
        recomendaciones = []
        
        if categoria == "Liviana":
            if horas_vuelo > 500:
                recomendaciones.append("Revisar sistema de combustible")
                recomendaciones.append("Inspección de hélice")
            if horas_vuelo > 1000:
                recomendaciones.append("Overhaul del motor")
        
        elif categoria == "Mediana":
            if horas_vuelo > 1000:
                recomendaciones.append("Inspección de sistemas hidráulicos")
                recomendaciones.append("Revisión de aviónica")
            if horas_vuelo > 2000:
                recomendaciones.append("Mantenimiento mayor de motores")
        
        else:  # Pesada
            if horas_vuelo > 2000:
                recomendaciones.append("Inspección estructural completa")
                recomendaciones.append("Revisión de sistemas de navegación")
            if horas_vuelo > 4000:
                recomendaciones.append("Overhaul completo requerido")
        
        if not recomendaciones:
            recomendaciones.append("Mantenimiento preventivo estándar")
        
        return recomendaciones
    
    def guardar_modelo(self):
        """Guardar modelo entrenado"""
        try:
            fecha = datetime.now().strftime("%Y%m%d_%H%M")
            
            # Guardar modelo principal
            joblib.dump(self.modelo, f'modelos_ia/modelo_aeronaves_{fecha}.pkl')
            
            # Guardar scaler y encoders
            joblib.dump(self.scaler, f'modelos_ia/scaler_{fecha}.pkl')
            joblib.dump(self.label_encoder_categoria, f'modelos_ia/encoder_categoria_{fecha}.pkl')
            joblib.dump(self.label_encoder_fabricante, f'modelos_ia/encoder_fabricante_{fecha}.pkl')
            
            # Guardar modelo actual (sobrescribir)
            joblib.dump(self.modelo, 'modelos_ia/modelo_actual.pkl')
            joblib.dump(self.scaler, 'modelos_ia/scaler_actual.pkl')
            joblib.dump(self.label_encoder_categoria, 'modelos_ia/encoder_categoria_actual.pkl')
            joblib.dump(self.label_encoder_fabricante, 'modelos_ia/encoder_fabricante_actual.pkl')
            
        except Exception as e:
            print(f"Error al guardar modelo: {e}")
    
    def cargar_modelo(self):
        """Cargar modelo previamente entrenado"""
        try:
            if os.path.exists('modelos_ia/modelo_actual.pkl'):
                self.modelo = joblib.load('modelos_ia/modelo_actual.pkl')
                self.scaler = joblib.load('modelos_ia/scaler_actual.pkl')
                self.label_encoder_categoria = joblib.load('modelos_ia/encoder_categoria_actual.pkl')
                self.label_encoder_fabricante = joblib.load('modelos_ia/encoder_fabricante_actual.pkl')
                self.fabricantes_conocidos = list(self.label_encoder_fabricante.classes_)
                self.modelo_entrenado = True
                return True
            else:
                return False
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            return False

class VentanaIAAeronaves(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Sistema de IA para Aeronaves")
        self.geometry("900x700")
        self.configure(bg='#ecf0f1')
        
        self.ia_sistema = SistemaIAAeronaves(parent)
        
        # Variables
        self.var_peso = tk.StringVar()
        self.var_horas = tk.StringVar()
        self.var_ano = tk.StringVar(value="2020")
        
        self.crear_interfaz()
        
        # Intentar cargar modelo existente
        if self.ia_sistema.cargar_modelo():
            self.lbl_estado.config(text="✅ Modelo cargado", fg="#2ecc71")
    
    def crear_interfaz(self):
        # Título
        tk.Label(self, text="🤖 Sistema de IA para Clasificación de Aeronaves", 
                font=('Arial', 18, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=20)
        
        # Frame principal con notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: Entrenamiento
        tab_entrenamiento = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(tab_entrenamiento, text="🎯 Entrenamiento")
        
        self.crear_tab_entrenamiento(tab_entrenamiento)
        
        # Tab 2: Predicción
        tab_prediccion = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(tab_prediccion, text="🔮 Predicción")
        
        self.crear_tab_prediccion(tab_prediccion)
        
        # Tab 3: Análisis Predictivo
        tab_analisis = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(tab_analisis, text="📊 Análisis Predictivo")
        
        self.crear_tab_analisis(tab_analisis)
    
    def crear_tab_entrenamiento(self, parent):
        # Estado del modelo
        estado_frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=2)
        estado_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(estado_frame, text="Estado del Modelo de IA", 
                font=('Arial', 14, 'bold'), bg='#34495e', fg='white').pack(pady=10)
        
        self.lbl_estado = tk.Label(estado_frame, text="❌ Modelo no entrenado", 
                                  font=('Arial', 12), bg='#34495e', fg='#e74c3c')
        self.lbl_estado.pack(pady=5)
        
        # Información
        info_text = """
        El sistema de IA analiza:
        • Peso MTOW de la aeronave
        • Horas de vuelo acumuladas  
        • Año de fabricación estimado
        
        Y predice automáticamente la categoría correcta
        """
        
        tk.Label(parent, text=info_text, font=('Arial', 11), 
                bg='#ecf0f1', fg='#2c3e50', justify='left').pack(pady=20)
        
        # Botón de entrenamiento
        tk.Button(parent, text="🚀 Entrenar Modelo de IA", 
                 command=self.entrenar_modelo,
                 bg='#3498db', fg='white', font=('Arial', 14, 'bold'),
                 width=25, height=2).pack(pady=20)
        
        # Progreso
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.pack(pady=10, padx=50, fill='x')
    
    def crear_tab_prediccion(self, parent):
        # Formulario de predicción
        form_frame = tk.Frame(parent, bg='#ecf0f1')
        form_frame.pack(pady=30)
        
        tk.Label(form_frame, text="Ingresa los datos de la aeronave:", 
                font=('Arial', 14, 'bold'), bg='#ecf0f1').grid(row=0, column=0, columnspan=2, pady=20)
        
        # Campos
        tk.Label(form_frame, text="Peso MTOW (kg):", bg='#ecf0f1').grid(row=1, column=0, sticky='w', pady=5)
        tk.Entry(form_frame, textvariable=self.var_peso, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Horas de Vuelo:", bg='#ecf0f1').grid(row=2, column=0, sticky='w', pady=5)
        tk.Entry(form_frame, textvariable=self.var_horas, width=20).grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Año de Fabricación:", bg='#ecf0f1').grid(row=3, column=0, sticky='w', pady=5)
        tk.Entry(form_frame, textvariable=self.var_ano, width=20).grid(row=3, column=1, padx=10, pady=5)
        
        # Botón de predicción
        tk.Button(form_frame, text="🔮 Predecir Categoría", 
                 command=self.hacer_prediccion,
                 bg='#2ecc71', fg='white', font=('Arial', 12, 'bold')).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Resultados
        self.resultado_frame = tk.Frame(parent, bg='#ecf0f1')
        self.resultado_frame.pack(pady=20)
    
    def crear_tab_analisis(self, parent):
        # Selector de aeronave
        tk.Label(parent, text="Análisis Predictivo de Mantenimiento", 
                font=('Arial', 16, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        select_frame = tk.Frame(parent, bg='#ecf0f1')
        select_frame.pack(pady=20)
        
        tk.Label(select_frame, text="Seleccionar Aeronave:", bg='#ecf0f1').pack()
        
        aeronaves = self.parent.db.obtener_aeronaves()
        aeronave_values = [f"{a[0]}|{a[1]} - {a[2]}" for a in aeronaves]
        
        self.combo_aeronave = ttk.Combobox(select_frame, values=aeronave_values, width=40)
        self.combo_aeronave.pack(pady=10)
        
        tk.Button(select_frame, text="📊 Analizar", 
                 command=self.analizar_mantenimiento,
                 bg='#f39c12', fg='white', font=('Arial', 12)).pack(pady=10)
        
        # Frame para resultados del análisis
        self.analisis_frame = tk.Frame(parent, bg='#ecf0f1')
        self.analisis_frame.pack(fill='both', expand=True, pady=20)
    
    def entrenar_modelo(self):
        """Entrenar el modelo de IA"""
        self.progress.start()
        self.lbl_estado.config(text="🔄 Entrenando modelo...", fg="#f39c12")
        self.update()
        
        # Entrenar en hilo separado (simulado con after)
        self.after(100, self._entrenar_async)
    
    def _entrenar_async(self):
        """Función asíncrona para entrenamiento"""
        success = self.ia_sistema.entrenar_modelo()
        
        self.progress.stop()
        
        if success:
            self.lbl_estado.config(text="✅ Modelo entrenado exitosamente", fg="#2ecc71")
        else:
            self.lbl_estado.config(text="❌ Error en entrenamiento", fg="#e74c3c")
    
    def hacer_prediccion(self):
        """Realizar predicción con IA"""
        try:
            peso = float(self.var_peso.get())
            horas = float(self.var_horas.get())
            ano = int(self.var_ano.get()) if self.var_ano.get() else 2020
            
            categoria, confianza = self.ia_sistema.predecir_categoria(peso, horas, ano)
            
            if categoria:
                # Limpiar resultados anteriores
                for widget in self.resultado_frame.winfo_children():
                    widget.destroy()
                
                # Mostrar resultado
                resultado_title = tk.Label(self.resultado_frame, text="🎯 Resultado de la Predicción", 
                                         font=('Arial', 14, 'bold'), bg='#ecf0f1')
                resultado_title.pack(pady=10)
                
                # Categoría predicha
                color_categoria = {"Liviana": "#3498db", "Mediana": "#f39c12", "Pesada": "#e74c3c"}
                categoria_label = tk.Label(self.resultado_frame, 
                                         text=f"Categoría: {categoria}", 
                                         font=('Arial', 16, 'bold'),
                                         bg=color_categoria.get(categoria, "#95a5a6"),
                                         fg='white')
                categoria_label.pack(pady=5)
                
                # Confianza
                confianza_label = tk.Label(self.resultado_frame, 
                                         text=f"Confianza: {confianza:.1%}", 
                                         font=('Arial', 12), bg='#ecf0f1')
                confianza_label.pack(pady=5)
                
                # Sugerencias de fabricante
                fabricantes_sugeridos = self.ia_sistema.sugerir_fabricante(peso, categoria)
                sugerencias_text = "Fabricantes sugeridos: " + ", ".join(fabricantes_sugeridos)
                tk.Label(self.resultado_frame, text=sugerencias_text, 
                        font=('Arial', 11), bg='#ecf0f1', fg='#7f8c8d').pack(pady=5)
                
            else:
                messagebox.showerror("Error", "No se pudo realizar la predicción")
                
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")
    
    def analizar_mantenimiento(self):
        """Realizar análisis predictivo de mantenimiento"""
        if not self.combo_aeronave.get():
            messagebox.showwarning("Advertencia", "Selecciona una aeronave")
            return
        
        try:
            aeronave_id = int(self.combo_aeronave.get().split("|")[0])
            analisis = self.ia_sistema.analizar_mantenimiento_predictivo(aeronave_id)
            
            if analisis:
                # Limpiar análisis anterior
                for widget in self.analisis_frame.winfo_children():
                    widget.destroy()
                
                # Mostrar análisis
                tk.Label(self.analisis_frame, text="📊 Análisis Predictivo", 
                        font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
                
                # Panel de urgencia
                urgencia_frame = tk.Frame(self.analisis_frame, bg=analisis['color'], relief='raised', bd=3)
                urgencia_frame.pack(fill='x', padx=20, pady=10)
                
                tk.Label(urgencia_frame, text=f"URGENCIA: {analisis['urgencia']}", 
                        font=('Arial', 14, 'bold'), bg=analisis['color'], fg='white').pack(pady=10)
                
                tk.Label(urgencia_frame, text=f"Horas restantes: {analisis['horas_restantes']:.1f}", 
                        font=('Arial', 12), bg=analisis['color'], fg='white').pack(pady=5)
                
                # Costo estimado
                tk.Label(self.analisis_frame, 
                        text=f"💰 Costo estimado: Bs {analisis['costo_estimado']:,.2f}", 
                        font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(pady=10)
                
                # Recomendaciones
                tk.Label(self.analisis_frame, text="🔧 Recomendaciones:", 
                        font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(pady=(20, 5))
                
                for rec in analisis['recomendaciones']:
                    tk.Label(self.analisis_frame, text=f"• {rec}", 
                            font=('Arial', 11), bg='#ecf0f1', anchor='w').pack(fill='x', padx=30)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis: {str(e)}")