# Base de Datos SQLite
import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_name="sgma_aeronaves.db"):
        self.db_name = db_name
        self.crear_tablas()
        self.insertar_datos_iniciales()
    
    def crear_conexion(self):
        """Crear conexión a la base de datos"""
        return sqlite3.connect(self.db_name)
    
    def crear_tablas(self):
        """Crear todas las tablas necesarias"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        # Tabla de aeronaves
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aeronaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT UNIQUE NOT NULL,
                modelo TEXT NOT NULL,
                fabricante TEXT NOT NULL,
                peso_mtow REAL NOT NULL,
                categoria TEXT NOT NULL,
                horas_vuelo REAL NOT NULL,
                hangar_id INTEGER,
                fecha_registro TEXT NOT NULL,
                FOREIGN KEY (hangar_id) REFERENCES hangares (id)
            )
        ''')
        
        # Tabla de hangares
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hangares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ubicacion TEXT NOT NULL,
                capacidad INTEGER NOT NULL,
                ocupacion INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de técnicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tecnicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                especialidad TEXT NOT NULL,
                licencia TEXT UNIQUE NOT NULL,
                activo BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Tabla de mantenimientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mantenimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aeronave_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                fecha_programada TEXT NOT NULL,
                tecnico_id INTEGER NOT NULL,
                descripcion TEXT,
                estado TEXT DEFAULT 'Programado',
                fecha_creacion TEXT NOT NULL,
                costo REAL DEFAULT 0,
                FOREIGN KEY (aeronave_id) REFERENCES aeronaves (id),
                FOREIGN KEY (tecnico_id) REFERENCES tecnicos (id)
            )
        ''')
        
        # Tabla de piezas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS piezas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                stock INTEGER NOT NULL DEFAULT 0,
                precio REAL NOT NULL,
                proveedor TEXT,
                fecha_actualizacion TEXT NOT NULL
            )
        ''')
        
        # Tabla de uso de piezas en mantenimientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mantenimiento_piezas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mantenimiento_id INTEGER NOT NULL,
                pieza_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                FOREIGN KEY (mantenimiento_id) REFERENCES mantenimientos (id),
                FOREIGN KEY (pieza_id) REFERENCES piezas (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insertar_datos_iniciales(self):
        """Insertar datos iniciales si la base está vacía"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM hangares")
        if cursor.fetchone()[0] == 0:
            # Insertar hangares
            hangares_iniciales = [
                ("Hangar A", "El Alto", 5),
                ("Hangar B", "Santa Cruz", 3),
                ("Hangar C", "Cochabamba", 4),
                ("Hangar D", "Tarija", 2)
            ]
            cursor.executemany("INSERT INTO hangares (nombre, ubicacion, capacidad) VALUES (?, ?, ?)", 
                             hangares_iniciales)
            
            # Insertar técnicos
            tecnicos_iniciales = [
                ("Carlos Mendoza", "Motores", "AMT-001"),
                ("Ana Rodriguez", "Aviónica", "AMT-002"),
                ("Luis Vargas", "Estructural", "AMT-003"),
                ("Maria Gutierrez", "Sistemas Hidráulicos", "AMT-004"),
                ("Pedro Quispe", "Instrumentos", "AMT-005")
            ]
            cursor.executemany("INSERT INTO tecnicos (nombre, especialidad, licencia) VALUES (?, ?, ?)", 
                             tecnicos_iniciales)
            
            # Insertar piezas
            piezas_iniciales = [
                ("Filtro de Aceite", "Filtro para sistema de lubricación", 25, 150.0, "AeroPartes SA"),
                ("Batería", "Batería de 24V para sistemas eléctricos", 8, 800.0, "PowerAir Ltd"),
                ("Neumático Principal", "Neumático para tren principal", 12, 1200.0, "TireAero Inc"),
                ("Válvula Hidráulica", "Válvula para sistema hidráulico", 15, 350.0, "HydroTech"),
                ("Sensor de Temperatura", "Sensor para monitoreo de motores", 30, 250.0, "SensorAir")
            ]
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            cursor.executemany("INSERT INTO piezas (nombre, descripcion, stock, precio, proveedor, fecha_actualizacion) VALUES (?, ?, ?, ?, ?, ?)", 
                             [(p[0], p[1], p[2], p[3], p[4], fecha_actual) for p in piezas_iniciales])
            
            # Insertar aeronaves de ejemplo
            aeronaves_ejemplo = [
                ("CP-2501", "Boeing 737-800", "Boeing", 79000, "Pesada", 1250.5, 1),
                ("CP-2789", "Airbus A320", "Airbus", 73500, "Pesada", 890.2, 2),
                ("CP-1456", "Cessna 172", "Cessna", 1157, "Liviana", 320.8, 3)
            ]
            for aeronave in aeronaves_ejemplo:
                cursor.execute("""INSERT INTO aeronaves 
                               (matricula, modelo, fabricante, peso_mtow, categoria, horas_vuelo, hangar_id, fecha_registro) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                               (*aeronave, fecha_actual))
        
        conn.commit()
        conn.close()
    
    # Métodos para aeronaves
    def insertar_aeronave(self, matricula, modelo, fabricante, peso_mtow, categoria, horas_vuelo, hangar_id):
        """Insertar nueva aeronave"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        try:
            cursor.execute("""INSERT INTO aeronaves 
                           (matricula, modelo, fabricante, peso_mtow, categoria, horas_vuelo, hangar_id, fecha_registro) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (matricula, modelo, fabricante, peso_mtow, categoria, horas_vuelo, hangar_id, fecha_actual))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def obtener_aeronaves(self):
        """Obtener todas las aeronaves"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("""SELECT a.*, h.nombre as hangar_nombre 
                         FROM aeronaves a 
                         LEFT JOIN hangares h ON a.hangar_id = h.id""")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    def obtener_aeronave_por_id(self, aeronave_id):
        """Obtener aeronave específica por ID"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM aeronaves WHERE id = ?", (aeronave_id,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    
    # Métodos para hangares
    def obtener_hangares(self):
        """Obtener todos los hangares"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hangares")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    def obtener_hangar_por_nombre(self, nombre):
        """Obtener hangar por nombre"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hangares WHERE nombre = ?", (nombre,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    
    # Métodos para técnicos
    def obtener_tecnicos(self):
        """Obtener todos los técnicos activos"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tecnicos WHERE activo = TRUE")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    def obtener_tecnico_por_nombre(self, nombre):
        """Obtener técnico por nombre"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tecnicos WHERE nombre LIKE ?", (f"%{nombre}%",))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    
    # Métodos para mantenimientos
    def insertar_mantenimiento(self, aeronave_id, tipo, fecha_programada, tecnico_id, descripcion, costo=0):
        """Insertar nuevo mantenimiento"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cursor.execute("""INSERT INTO mantenimientos 
                       (aeronave_id, tipo, fecha_programada, tecnico_id, descripcion, fecha_creacion, costo) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                       (aeronave_id, tipo, fecha_programada, tecnico_id, descripcion, fecha_actual, costo))
        conn.commit()
        conn.close()
        return True
    
    def obtener_mantenimientos(self):
        """Obtener todos los mantenimientos con información relacionada"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("""SELECT m.*, a.matricula, a.modelo, t.nombre as tecnico_nombre 
                         FROM mantenimientos m 
                         JOIN aeronaves a ON m.aeronave_id = a.id 
                         JOIN tecnicos t ON m.tecnico_id = t.id 
                         ORDER BY m.fecha_programada DESC""")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    def obtener_mantenimientos_por_aeronave(self, aeronave_id):
        """Obtener mantenimientos de una aeronave específica"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("""SELECT m.*, t.nombre as tecnico_nombre 
                         FROM mantenimientos m 
                         JOIN tecnicos t ON m.tecnico_id = t.id 
                         WHERE m.aeronave_id = ? 
                         ORDER BY m.fecha_programada DESC""", (aeronave_id,))
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    # Métodos para piezas
    def obtener_piezas(self):
        """Obtener todas las piezas"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM piezas ORDER BY nombre")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    def actualizar_stock_pieza(self, pieza_id, nueva_cantidad):
        """Actualizar stock de una pieza"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE piezas SET stock = ?, fecha_actualizacion = ? WHERE id = ?", 
                      (nueva_cantidad, fecha_actual, pieza_id))
        conn.commit()
        conn.close()
        return True
    
    # Métodos para alertas
    def obtener_aeronaves_con_alertas(self):
        """Obtener aeronaves que requieren mantenimiento (más de cierta cantidad de horas)"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM aeronaves 
                         WHERE (categoria = 'Liviana' AND horas_vuelo > 100) 
                         OR (categoria = 'Mediana' AND horas_vuelo > 150) 
                         OR (categoria = 'Pesada' AND horas_vuelo > 200)""")
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    
    # Métodos para estadísticas
    def obtener_estadisticas_generales(self):
        """Obtener estadísticas generales del sistema"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        estadisticas = {}
        
        # Total aeronaves por categoría
        cursor.execute("SELECT categoria, COUNT(*) FROM aeronaves GROUP BY categoria")
        estadisticas['aeronaves_por_categoria'] = dict(cursor.fetchall())
        
        # Mantenimientos por estado
        cursor.execute("SELECT estado, COUNT(*) FROM mantenimientos GROUP BY estado")
        estadisticas['mantenimientos_por_estado'] = dict(cursor.fetchall())
        
        # Costos totales
        cursor.execute("SELECT SUM(costo) FROM mantenimientos")
        resultado = cursor.fetchone()
        estadisticas['costo_total_mantenimientos'] = resultado[0] if resultado[0] else 0
        
        conn.close()
        return estadisticas
    
    def cerrar_conexion(self):
        """Cerrar conexión (no es necesario con context managers, pero útil para cleanup)"""
        pass