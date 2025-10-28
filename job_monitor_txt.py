"""
JOB MONITOR - Sistema de monitoreo de portales de empleo
Guarda ofertas en archivo TXT local
Autor: Tu nombre
Fecha: 2025
"""

import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import json
import sqlite3

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

class JobMonitorConfig:
    """Configuración centralizada del programa"""
    
    # Base de datos
    DB_NAME = "job_monitor.db"
    OFERTAS_FILE = "ofertas_nuevas.txt"
    RESUMEN_FILE = "resumen_diario.txt"
    
    # Criterios de búsqueda
    CRITERIOS = {
        "salario_min": 25000,
        "salario_max": 32000,
        "tipo_trabajo": "remoto",
        "rol": "backend",
        "palabras_clave": [
            "java", "spring boot", "backend", "api",
            "microservices", "remote", "remoto"
        ]
    }


# ============================================================================
# MANEJO DE BASE DE DATOS
# ============================================================================

class DatabaseManager:
    """Gestiona la base de datos SQLite local"""
    
    def __init__(self, db_name=JobMonitorConfig.DB_NAME):
        self.db_name = db_name
        self.crear_tablas()
    
    def crear_tablas(self):
        """Crea las tablas si no existen"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de ofertas ya procesadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ofertas (
                id TEXT PRIMARY KEY,
                titulo TEXT,
                empresa TEXT,
                url TEXT,
                salario TEXT,
                portal TEXT,
                fecha_publicacion TIMESTAMP,
                fecha_encontrada TIMESTAMP
            )
        """)
        
        # Tabla de log de actividad
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP,
                portal TEXT,
                accion TEXT,
                detalles TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def oferta_existe(self, oferta_id):
        """Verifica si la oferta ya está en la BD"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ofertas WHERE id = ?", (oferta_id,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None
    
    def guardar_oferta(self, oferta):
        """Guarda una nueva oferta en la BD"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ofertas (id, titulo, empresa, url, salario, portal, 
                                fecha_publicacion, fecha_encontrada)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            oferta["id"],
            oferta["titulo"],
            oferta["empresa"],
            oferta["url"],
            oferta["salario"],
            oferta["portal"],
            oferta["fecha_publicacion"],
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def agregar_log(self, portal, accion, detalles=""):
        """Registra actividad en logs"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (fecha, portal, accion, detalles)
            VALUES (?, ?, ?, ?)
        """, (datetime.now(), portal, accion, detalles))
        conn.commit()
        conn.close()
    
    def obtener_ofertas_del_dia(self):
        """Obtiene ofertas encontradas hoy"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        hoy = datetime.now().date()
        cursor.execute("""
            SELECT titulo, empresa, url, salario, portal 
            FROM ofertas 
            WHERE DATE(fecha_encontrada) = ?
        """, (hoy,))
        ofertas = cursor.fetchall()
        conn.close()
        return ofertas


# ============================================================================
# MANEJO DE ARCHIVOS TXT
# ============================================================================

class FileManager:
    """Gestiona guardado de ofertas en archivos TXT"""
    
    @staticmethod
    def guardar_oferta_txt(oferta):
        """Guarda una oferta individual en TXT"""
        try:
            with open(JobMonitorConfig.OFERTAS_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"🎯 NUEVA OFERTA ENCONTRADA\n")
                f.write(f"{'='*70}\n")
                f.write(f"📌 Título: {oferta['titulo']}\n")
                f.write(f"🏢 Empresa: {oferta['empresa']}\n")
                f.write(f"💼 Portal: {oferta['portal'].upper()}\n")
                f.write(f"💰 Salario: {oferta['salario']}\n")
                f.write(f"🔗 URL: {oferta['url']}\n")
                f.write(f"⏰ Encontrada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"{'='*70}\n\n")
            
            print(f"✅ Oferta guardada en {JobMonitorConfig.OFERTAS_FILE}")
            return True
        
        except Exception as e:
            print(f"❌ Error guardando oferta: {e}")
            return False
    
    @staticmethod
    def guardar_resumen_txt(ofertas_nuevas):
        """Guarda resumen diario en TXT"""
        try:
            with open(JobMonitorConfig.RESUMEN_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"📊 RESUMEN DIARIO - {datetime.now().strftime('%d/%m/%Y')}\n")
                f.write(f"{'='*70}\n")
                
                if not ofertas_nuevas:
                    f.write("❌ No hay nuevas ofertas hoy\n")
                else:
                    f.write(f"✅ Se encontraron {len(ofertas_nuevas)} ofertas nuevas:\n\n")
                    
                    for i, oferta in enumerate(ofertas_nuevas, 1):
                        f.write(f"{i}. {oferta['titulo']}\n")
                        f.write(f"   🏢 {oferta['empresa']}\n")
                        f.write(f"   💰 {oferta['salario']}\n")
                        f.write(f"   🔗 {oferta['url']}\n")
                        f.write(f"   🌐 {oferta['portal']}\n\n")
                
                f.write(f"{'='*70}\n\n")
            
            print(f"✅ Resumen guardado en {JobMonitorConfig.RESUMEN_FILE}")
            return True
        
        except Exception as e:
            print(f"❌ Error guardando resumen: {e}")
            return False
    
    @staticmethod
    def limpiar_ofertas():
        """Borra el archivo de ofertas nuevas"""
        try:
            with open(JobMonitorConfig.OFERTAS_FILE, "w", encoding="utf-8") as f:
                f.write(f"JOB MONITOR - OFERTAS NUEVAS\n")
                f.write(f"{'='*70}\n")
                f.write(f"Creado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"{'='*70}\n\n")
            print(f"✅ Archivo {JobMonitorConfig.OFERTAS_FILE} limpiado")
        except Exception as e:
            print(f"❌ Error limpiando archivo: {e}")


# ============================================================================
# SCRAPING DE PORTALES
# ============================================================================

class PortalScraper:
    """Extrae ofertas de diferentes portales"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.db = DatabaseManager()
    
    def buscar_en_indeed(self):
        """Busca ofertas en Indeed"""
        print("🔍 Buscando en Indeed...")
        ofertas = []
        
        try:
            url = "https://es.indeed.com/jobs"
            parametros = {
                "q": "backend remote java",
                "l": "Spain",
                "radius": "0",
                "jt": "fulltime"
            }
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                jobs = soup.find_all("div", class_="job_seen_beacon")
                
                for job in jobs[:10]:  # Primeras 10
                    try:
                        titulo = job.find("h2", class_="jobTitle")
                        if not titulo:
                            continue
                        titulo = titulo.text.strip()
                        
                        empresa = job.find("span", class_="companyName")
                        empresa = empresa.text.strip() if empresa else "Desconocida"
                        
                        url_job = job.find("a", class_="jcs-JobTitle")
                        url_job = url_job.get("href", "") if url_job else ""
                        
                        salario_elem = job.find("span", class_="salary-snippet")
                        salario = salario_elem.text.strip() if salario_elem else "No especificado"
                        
                        oferta_id = f"indeed_{titulo}_{empresa}".replace(" ", "_")
                        
                        oferta = {
                            "id": oferta_id,
                            "titulo": titulo,
                            "empresa": empresa,
                            "url": f"https://es.indeed.com{url_job}" if url_job else "N/A",
                            "salario": salario,
                            "portal": "indeed",
                            "fecha_publicacion": datetime.now()
                        }
                        
                        ofertas.append(oferta)
                    
                    except Exception as e:
                        print(f"⚠️ Error extrayendo oferta: {e}")
                
                self.db.agregar_log(
                    "indeed",
                    "busqueda",
                    f"Se encontraron {len(ofertas)} ofertas"
                )
                print(f"   ✅ {len(ofertas)} ofertas en Indeed")
        
        except Exception as e:
            print(f"❌ Error en Indeed: {e}")
            self.db.agregar_log("indeed", "error", str(e))
        
        return ofertas
    
    def buscar_en_infojobs(self):
        """Busca ofertas en InfoJobs"""
        print("🔍 Buscando en InfoJobs...")
        ofertas = []
        
        try:
            url = "https://www.infojobs.net/search"
            parametros = {
                "q": "backend remoto java",
                "c": "47"  # Código de España
            }
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                jobs = soup.find_all("article", class_="offer")
                
                for job in jobs[:10]:
                    try:
                        titulo_elem = job.find("h2")
                        if not titulo_elem:
                            continue
                        titulo = titulo_elem.text.strip()
                        
                        empresa_elem = job.find("span", class_="company")
                        empresa = empresa_elem.text.strip() if empresa_elem else "Desconocida"
                        
                        url_elem = job.find("a", class_="link")
                        url_job = url_elem.get("href", "") if url_elem else ""
                        
                        oferta_id = f"infojobs_{titulo}_{empresa}".replace(" ", "_")
                        
                        oferta = {
                            "id": oferta_id,
                            "titulo": titulo,
                            "empresa": empresa,
                            "url": f"https://infojobs.net{url_job}" if url_job else "N/A",
                            "salario": "No especificado",
                            "portal": "infojobs",
                            "fecha_publicacion": datetime.now()
                        }
                        
                        ofertas.append(oferta)
                    
                    except Exception as e:
                        print(f"⚠️ Error extrayendo oferta: {e}")
                
                self.db.agregar_log(
                    "infojobs",
                    "busqueda",
                    f"Se encontraron {len(ofertas)} ofertas"
                )
                print(f"   ✅ {len(ofertas)} ofertas en InfoJobs")
        
        except Exception as e:
            print(f"❌ Error en InfoJobs: {e}")
            self.db.agregar_log("infojobs", "error", str(e))
        
        return ofertas
    
    def buscar_en_computrabajo(self):
        """Busca ofertas en Computrabajo"""
        print("🔍 Buscando en Computrabajo...")
        ofertas = []
        
        try:
            url = "https://www.computrabajo.com/search/jobs"
            parametros = {
                "q": "backend remote java",
                "location": "Spain"
            }
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                jobs = soup.find_all("div", class_="offer-item")
                
                for job in jobs[:10]:
                    try:
                        titulo_elem = job.find("h2")
                        if not titulo_elem:
                            continue
                        titulo = titulo_elem.text.strip()
                        
                        empresa_elem = job.find("h3")
                        empresa = empresa_elem.text.strip() if empresa_elem else "Desconocida"
                        
                        url_elem = job.find("a")
                        url_job = url_elem.get("href", "") if url_elem else ""
                        
                        oferta_id = f"computrabajo_{titulo}_{empresa}".replace(" ", "_")
                        
                        oferta = {
                            "id": oferta_id,
                            "titulo": titulo,
                            "empresa": empresa,
                            "url": url_job if url_job.startswith("http") else f"https://computrabajo.com{url_job}",
                            "salario": "No especificado",
                            "portal": "computrabajo",
                            "fecha_publicacion": datetime.now()
                        }
                        
                        ofertas.append(oferta)
                    
                    except Exception as e:
                        print(f"⚠️ Error extrayendo oferta: {e}")
                
                self.db.agregar_log(
                    "computrabajo",
                    "busqueda",
                    f"Se encontraron {len(ofertas)} ofertas"
                )
                print(f"   ✅ {len(ofertas)} ofertas en Computrabajo")
        
        except Exception as e:
            print(f"❌ Error en Computrabajo: {e}")
            self.db.agregar_log("computrabajo", "error", str(e))
        
        return ofertas
    
    def obtener_todas_las_ofertas(self):
        """Ejecuta búsqueda en todos los portales"""
        todas_ofertas = []
        
        todas_ofertas.extend(self.buscar_en_indeed())
        todas_ofertas.extend(self.buscar_en_infojobs())
        todas_ofertas.extend(self.buscar_en_computrabajo())
        
        return todas_ofertas


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

class JobMonitor:
    """Coordina el monitoreo completo"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = PortalScraper()
        self.file_manager = FileManager()
    
    def ejecutar_monitoreo(self):
        """Ejecuta una ronda completa de monitoreo"""
        
        print(f"\n{'='*70}")
        print(f"🚀 INICIANDO MONITOREO: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Obtener ofertas de todos los portales
        todas_ofertas = self.scraper.obtener_todas_las_ofertas()
        print(f"\n📊 Total de ofertas encontradas: {len(todas_ofertas)}")
        
        ofertas_nuevas = []
        
        # Procesar cada oferta
        for oferta in todas_ofertas:
            if not self.db.oferta_existe(oferta["id"]):
                # Oferta nueva - guardar y guardar en TXT
                self.db.guardar_oferta(oferta)
                self.file_manager.guardar_oferta_txt(oferta)
                ofertas_nuevas.append(oferta)
            else:
                print(f"⏭️  Oferta duplicada: {oferta['titulo']}")
        
        # Resumen
        if ofertas_nuevas:
            print(f"\n✅ {len(ofertas_nuevas)} ofertas nuevas encontradas y guardadas")
        else:
            print("\n⏭️  No hay ofertas nuevas en este monitoreo")
        
        print(f"\n{'='*70}\n")
    
    def generar_resumen_diario(self):
        """Genera resumen diario de ofertas"""
        print(f"\n📊 Generando resumen diario...")
        
        ofertas_hoy = self.db.obtener_ofertas_del_dia()
        
        if ofertas_hoy:
            ofertas_dict = [
                {
                    "titulo": o[0],
                    "empresa": o[1],
                    "url": o[2],
                    "salario": o[3],
                    "portal": o[4]
                }
                for o in ofertas_hoy
            ]
            self.file_manager.guardar_resumen_txt(ofertas_dict)
            print(f"✅ Resumen guardado: {len(ofertas_hoy)} ofertas del día")
        else:
            print("⏭️  No hay ofertas del día para resumir")
    
    def programar(self):
        """Programa el monitoreo automático"""
        
        print("\n📅 Programando monitoreo automático...\n")
        
        # Limpiar archivo de ofertas al iniciar
        self.file_manager.limpiar_ofertas()
        
        # Monitorear cada 2 horas
        schedule.every(2).hours.do(self.ejecutar_monitoreo)
        
        # Resumen diario a las 9:00 PM
        schedule.every().day.at("21:00").do(self.generar_resumen_diario)
        
        print("✅ Programación completada")
        print("⏰ Monitoreo cada 2 horas")
        print(f"📊 Resumen diario a las 21:00 en {JobMonitorConfig.RESUMEN_FILE}\n")
        
        print(f"Archivos de salida:")
        print(f"  📄 Ofertas nuevas: {JobMonitorConfig.OFERTAS_FILE}")
        print(f"  📄 Resumen diario: {JobMonitorConfig.RESUMEN_FILE}")
        print(f"  📄 BD de control: {JobMonitorConfig.DB_NAME}\n")
        
        # Mantener el programa corriendo
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            print("\n\n👋 Monitoreo detenido por el usuario")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     JOB MONITOR - Backend Remote      ║
    ║  Sistema de Monitoreo a Archivos TXT  ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("⚙️  Inicializando...\n")
    
    monitor = JobMonitor()
    
    # Opción 1: Ejecutar una sola vez
    print("Selecciona una opción:")
    print("1️⃣  Ejecutar monitoreo ahora (una sola vez)")
    print("2️⃣  Programar monitoreo automático (24/7)")
    print("3️⃣  Salir\n")
    
    opcion = input("Tu opción (1-3): ").strip()
    
    if opcion == "1":
        monitor.ejecutar_monitoreo()
        print("✅ Monitoreo completado")
        print(f"Ver ofertas en: {JobMonitorConfig.OFERTAS_FILE}")
    elif opcion == "2":
        monitor.programar()
    else:
        print("👋 Saliendo...")