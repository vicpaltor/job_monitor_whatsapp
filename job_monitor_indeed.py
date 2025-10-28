"""
JOB MONITOR - VERSIÓN INDEED
Monitoreo de ofertas en Indeed con Selenium
Guarda ofertas en archivo TXT
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import sqlite3
import schedule

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

class JobMonitorConfig:
    """Configuración centralizada del programa"""
    
    DB_NAME = "job_monitor.db"
    OFERTAS_FILE = "ofertas_nuevas.txt"
    RESUMEN_FILE = "resumen_diario.txt"


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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ofertas (
                id TEXT PRIMARY KEY,
                titulo TEXT,
                empresa TEXT,
                url TEXT,
                salario TEXT,
                fecha_encontrada TIMESTAMP
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
            INSERT INTO ofertas (id, titulo, empresa, url, salario, fecha_encontrada)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            oferta["id"],
            oferta["titulo"],
            oferta["empresa"],
            oferta["url"],
            oferta["salario"],
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def obtener_ofertas_del_dia(self):
        """Obtiene ofertas encontradas hoy"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        hoy = datetime.now().date()
        cursor.execute("""
            SELECT titulo, empresa, url, salario
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
                f.write(f"💰 Salario: {oferta['salario']}\n")
                f.write(f"🔗 URL: {oferta['url']}\n")
                f.write(f"⏰ Encontrada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"{'='*70}\n\n")
            
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
                        f.write(f"   🔗 {oferta['url']}\n\n")
                
                f.write(f"{'='*70}\n\n")
            
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
        except Exception as e:
            print(f"❌ Error limpiando archivo: {e}")


# ============================================================================
# SCRAPING CON SELENIUM
# ============================================================================

class IndeedScraper:
    """Scraper de Indeed con Selenium"""
    
    def __init__(self, titulo_busqueda):
        self.titulo_busqueda = titulo_busqueda
        self.db = DatabaseManager()
        
        # Configurar opciones del navegador
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    
    def obtener_ofertas(self):
        """Extrae ofertas de Indeed"""
        print(f"🔍 Buscando en Indeed: '{self.titulo_busqueda}'...\n")
        
        driver = None
        ofertas = []
        
        try:
            # Iniciar navegador
            print("🚀 Abriendo navegador...\n")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Navegar a Indeed
            url = f"https://es.indeed.com/jobs?q={self.titulo_busqueda}&l=Spain"
            print(f"📍 Navegando a: {url}\n")
            driver.get(url)
            
            # Esperar a que cargue
            print("⏳ Esperando que cargue la página...")
            time.sleep(3)
            print("✅ Página cargada\n")
            
            # Obtener ofertas
            print("🔎 Extrayendo ofertas...\n")
            
            try:
                jobs = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
            except:
                jobs = []
            
            print(f"   Ofertas encontradas: {len(jobs)}\n")
            
            # Procesar cada oferta
            for i, job in enumerate(jobs, 1):
                try:
                    # Título
                    title_elem = job.find_element(By.TAG_NAME, "h2")
                    titulo = title_elem.text.strip()
                    
                    # Empresa
                    try:
                        company_elem = job.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
                        empresa = company_elem.text.strip()
                    except:
                        empresa = "Desconocida"
                    
                    # URL
                    try:
                        link_elem = job.find_element(By.TAG_NAME, "a")
                        url_job = link_elem.get_attribute("href")
                    except:
                        url_job = "N/A"
                    
                    # Salario
                    try:
                        salary_elem = job.find_element(By.CSS_SELECTOR, "span.salary-snippet")
                        salario = salary_elem.text.strip()
                    except:
                        salario = "No especificado"
                    
                    # Crear ID único
                    oferta_id = f"indeed_{titulo}_{empresa}".replace(" ", "_").lower()
                    
                    oferta = {
                        "id": oferta_id,
                        "titulo": titulo,
                        "empresa": empresa,
                        "url": url_job,
                        "salario": salario
                    }
                    
                    ofertas.append(oferta)
                    
                    print(f"   {i}. {titulo}")
                    print(f"      🏢 {empresa}")
                    print(f"      💰 {salario}\n")
                
                except Exception as e:
                    print(f"   ⚠️ Error extrayendo oferta {i}: {e}\n")
            
            print(f"\n✅ Total extraído: {len(ofertas)} ofertas\n")
            
            return ofertas
        
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            return []
        
        finally:
            if driver:
                print("🔚 Cerrando navegador...")
                time.sleep(1)
                driver.quit()


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

class JobMonitor:
    """Coordina el monitoreo completo"""
    
    def __init__(self, titulo_busqueda):
        self.titulo_busqueda = titulo_busqueda
        self.db = DatabaseManager()
        self.scraper = IndeedScraper(titulo_busqueda)
        self.file_manager = FileManager()
    
    def ejecutar_monitoreo(self):
        """Ejecuta una ronda completa de monitoreo"""
        
        print(f"\n{'='*70}")
        print(f"🚀 INICIANDO MONITOREO: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Obtener ofertas
        todas_ofertas = self.scraper.obtener_ofertas()
        
        ofertas_nuevas = []
        
        # Procesar cada oferta
        for oferta in todas_ofertas:
            if not self.db.oferta_existe(oferta["id"]):
                # Oferta nueva - guardar
                self.db.guardar_oferta(oferta)
                self.file_manager.guardar_oferta_txt(oferta)
                ofertas_nuevas.append(oferta)
                print(f"✅ Guardada: {oferta['titulo']}")
            else:
                print(f"⏭️  Duplicada: {oferta['titulo']}")
        
        # Resumen
        if ofertas_nuevas:
            print(f"\n✅ {len(ofertas_nuevas)} ofertas nuevas encontradas y guardadas")
        else:
            print("\n⏭️  No hay ofertas nuevas en este monitoreo")
        
        print(f"\n{'='*70}\n")
    
    def generar_resumen_diario(self):
        """Genera resumen diario de ofertas"""
        print(f"\n📊 Generando resumen diario...\n")
        
        ofertas_hoy = self.db.obtener_ofertas_del_dia()
        
        if ofertas_hoy:
            ofertas_dict = [
                {
                    "titulo": o[0],
                    "empresa": o[1],
                    "url": o[2],
                    "salario": o[3]
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
        print(f"  📄 Resumen diario: {JobMonitorConfig.RESUMEN_FILE}\n")
        
        # Mantener el programa corriendo
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoreo detenido por el usuario")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     JOB MONITOR - Indeed Only         ║
    ║  Monitoreo a Archivos TXT             ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("⚙️  Inicializando...\n")
    
    # Pedir título de búsqueda
    titulo_busqueda = input("Ingresa el título a buscar (ej: 'backend remote'): ").strip()
    
    if not titulo_busqueda:
        titulo_busqueda = "backend remote java"
        print(f"⚠️  Usando búsqueda por defecto: '{titulo_busqueda}'\n")
    else:
        print(f"✅ Búsqueda configurada: '{titulo_busqueda}'\n")
    
    monitor = JobMonitor(titulo_busqueda)
    
    # Opciones
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