"""
JOB MONITOR - VERSIÓN CON SELENIUM (Navegador Real)
Abre el navegador y scrappea en tiempo real
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE SELENIUM
# ============================================================================

class SeleniumScraper:
    """Scraper con Selenium que abre navegador real"""
    
    def __init__(self):
        # Configurar opciones del navegador
        self.chrome_options = Options()
        # NO usar headless para VER lo que está pasando
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent realista
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    
    def test_indeed(self, titulo_busqueda):
        """Prueba Indeed con Selenium"""
        print("\n" + "="*70)
        print(f"🧪 PROBANDO INDEED (Navegador Real)")
        print("="*70 + "\n")
        
        driver = None
        try:
            # Inicializar driver
            print("🚀 Abriendo navegador Chrome...\n")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Construcción de URL
            url = f"https://es.indeed.com/jobs?q={titulo_busqueda}&l=Spain"
            print(f"📍 Navegando a: {url}\n")
            
            driver.get(url)
            
            # Esperar a que cargue la página
            print("⏳ Esperando que cargue la página...")
            time.sleep(3)
            
            print("✅ Página cargada\n")
            
            # Obtener información de la página
            print("🔎 Analizando página...\n")
            
            # Obtener título
            title = driver.title
            print(f"   • Título de página: {title}")
            
            # Buscar ofertas con diferentes selectores
            print(f"\n   Buscando ofertas:\n")
            
            try:
                # Selector 1
                jobs1 = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
                print(f"   • Selector 1 (div.job_seen_beacon): {len(jobs1)} ofertas")
            except:
                jobs1 = []
                print(f"   • Selector 1 (div.job_seen_beacon): 0 ofertas")
            
            try:
                # Selector 2
                jobs2 = driver.find_elements(By.CSS_SELECTOR, "div.job-tile")
                print(f"   • Selector 2 (div.job-tile): {len(jobs2)} ofertas")
            except:
                jobs2 = []
                print(f"   • Selector 2 (div.job-tile): 0 ofertas")
            
            try:
                # Selector 3
                jobs3 = driver.find_elements(By.TAG_NAME, "article")
                print(f"   • Selector 3 (article): {len(jobs3)} ofertas")
            except:
                jobs3 = []
                print(f"   • Selector 3 (article): 0 ofertas")
            
            try:
                # Selector 4 - Más general
                jobs4 = driver.find_elements(By.CSS_SELECTOR, "[data-testid='job-card']")
                print(f"   • Selector 4 (data-testid): {len(jobs4)} ofertas")
            except:
                jobs4 = []
                print(f"   • Selector 4 (data-testid): 0 ofertas")
            
            # Usar el selector que más resultados dio
            all_jobs = max([jobs1, jobs2, jobs3, jobs4], key=len)
            total = len(all_jobs)
            
            print(f"\n✅ Total de ofertas encontradas: {total}\n")
            
            if total > 0:
                print("📋 Primeras 3 ofertas:\n")
                
                for i, job in enumerate(all_jobs[:3], 1):
                    try:
                        # Intenta extraer información
                        title_elem = job.find_element(By.TAG_NAME, "h2")
                        titulo = title_elem.text
                        
                        company_elem = job.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
                        empresa = company_elem.text
                        
                        print(f"   {i}. {titulo}")
                        print(f"      🏢 {empresa}\n")
                    except:
                        print(f"   {i}. [Info no disponible]\n")
            
            # Captura de pantalla
            screenshot_file = f"indeed_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_file)
            print(f"📸 Screenshot guardado: {screenshot_file}\n")
            
            # Guardar HTML
            html_file = "debug_indeed.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source[:10000])
            print(f"📄 HTML guardado: {html_file}\n")
            
            print("✅ INDEED: OK\n")
            return total > 0
        
        except Exception as e:
            print(f"❌ ERROR en Indeed: {e}\n")
            return False
        
        finally:
            if driver:
                print("🔚 Cerrando navegador...")
                time.sleep(2)
                driver.quit()
    
    def test_infojobs(self, titulo_busqueda):
        """Prueba InfoJobs con Selenium"""
        print("\n" + "="*70)
        print(f"🧪 PROBANDO INFOJOBS (Navegador Real)")
        print("="*70 + "\n")
        
        driver = None
        try:
            print("🚀 Abriendo navegador Chrome...\n")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            url = f"https://www.infojobs.net/search?q={titulo_busqueda}&c=47"
            print(f"📍 Navegando a: {url}\n")
            
            driver.get(url)
            
            print("⏳ Esperando que cargue la página...")
            time.sleep(3)
            
            print("✅ Página cargada\n")
            
            print("🔎 Analizando página...\n")
            
            title = driver.title
            print(f"   • Título de página: {title}\n")
            
            print(f"   Buscando ofertas:\n")
            
            try:
                jobs1 = driver.find_elements(By.CSS_SELECTOR, "article.offer")
                print(f"   • Selector 1 (article.offer): {len(jobs1)} ofertas")
            except:
                jobs1 = []
                print(f"   • Selector 1 (article.offer): 0 ofertas")
            
            try:
                jobs2 = driver.find_elements(By.CSS_SELECTOR, "div.offer")
                print(f"   • Selector 2 (div.offer): {len(jobs2)} ofertas")
            except:
                jobs2 = []
                print(f"   • Selector 2 (div.offer): 0 ofertas")
            
            try:
                jobs3 = driver.find_elements(By.TAG_NAME, "article")
                print(f"   • Selector 3 (article genérico): {len(jobs3)} ofertas")
            except:
                jobs3 = []
                print(f"   • Selector 3 (article genérico): 0 ofertas")
            
            all_jobs = max([jobs1, jobs2, jobs3], key=len)
            total = len(all_jobs)
            
            print(f"\n✅ Total de ofertas encontradas: {total}\n")
            
            if total > 0:
                print("📋 Primeras 3 ofertas:\n")
                
                for i, job in enumerate(all_jobs[:3], 1):
                    try:
                        title_elem = job.find_element(By.TAG_NAME, "h2")
                        titulo = title_elem.text
                        
                        company_elem = job.find_element(By.CSS_SELECTOR, "span.company")
                        empresa = company_elem.text
                        
                        print(f"   {i}. {titulo}")
                        print(f"      🏢 {empresa}\n")
                    except:
                        print(f"   {i}. [Info no disponible]\n")
            
            screenshot_file = f"infojobs_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_file)
            print(f"📸 Screenshot guardado: {screenshot_file}\n")
            
            html_file = "debug_infojobs.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source[:10000])
            print(f"📄 HTML guardado: {html_file}\n")
            
            print("✅ INFOJOBS: OK\n")
            return total > 0
        
        except Exception as e:
            print(f"❌ ERROR en InfoJobs: {e}\n")
            return False
        
        finally:
            if driver:
                print("🔚 Cerrando navegador...")
                time.sleep(2)
                driver.quit()
    
    def test_computrabajo(self, titulo_busqueda):
        """Prueba Computrabajo con Selenium"""
        print("\n" + "="*70)
        print(f"🧪 PROBANDO COMPUTRABAJO (Navegador Real)")
        print("="*70 + "\n")
        
        driver = None
        try:
            print("🚀 Abriendo navegador Chrome...\n")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            url = f"https://www.computrabajo.com/search/jobs?q={titulo_busqueda}&location=Spain"
            print(f"📍 Navegando a: {url}\n")
            
            driver.get(url)
            
            print("⏳ Esperando que cargue la página...")
            time.sleep(3)
            
            print("✅ Página cargada\n")
            
            print("🔎 Analizando página...\n")
            
            title = driver.title
            print(f"   • Título de página: {title}\n")
            
            print(f"   Buscando ofertas:\n")
            
            try:
                jobs1 = driver.find_elements(By.CSS_SELECTOR, "div.offer-item")
                print(f"   • Selector 1 (div.offer-item): {len(jobs1)} ofertas")
            except:
                jobs1 = []
                print(f"   • Selector 1 (div.offer-item): 0 ofertas")
            
            try:
                jobs2 = driver.find_elements(By.CSS_SELECTOR, "div.job")
                print(f"   • Selector 2 (div.job): {len(jobs2)} ofertas")
            except:
                jobs2 = []
                print(f"   • Selector 2 (div.job): 0 ofertas")
            
            all_jobs = max([jobs1, jobs2], key=len)
            total = len(all_jobs)
            
            print(f"\n✅ Total de ofertas encontradas: {total}\n")
            
            if total > 0:
                print("📋 Primeras 3 ofertas:\n")
                
                for i, job in enumerate(all_jobs[:3], 1):
                    try:
                        title_elem = job.find_element(By.TAG_NAME, "h2")
                        titulo = title_elem.text
                        
                        print(f"   {i}. {titulo}\n")
                    except:
                        print(f"   {i}. [Info no disponible]\n")
            
            screenshot_file = f"computrabajo_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_file)
            print(f"📸 Screenshot guardado: {screenshot_file}\n")
            
            html_file = "debug_computrabajo.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source[:10000])
            print(f"📄 HTML guardado: {html_file}\n")
            
            print("✅ COMPUTRABAJO: OK\n")
            return total > 0
        
        except Exception as e:
            print(f"❌ ERROR en Computrabajo: {e}\n")
            return False
        
        finally:
            if driver:
                print("🔚 Cerrando navegador...")
                time.sleep(2)
                driver.quit()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║   JOB MONITOR - MODO SELENIUM        ║
    ║  Scraping con Navegador Real          ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("\n⚙️  Inicializando...\n")
    
    # Verificar que Selenium esté instalado
    try:
        from selenium import webdriver
        print("✅ Selenium instalado\n")
    except ImportError:
        print("❌ Selenium no está instalado")
        print("\nInstala con:")
        print("   pip install selenium\n")
        exit()
    
    # Pedir título de búsqueda
    titulo = input("Ingresa el título a buscar (ej: 'backend remote'): ").strip()
    
    if not titulo:
        titulo = "backend remote java"
        print(f"⚠️  Usando búsqueda por defecto: '{titulo}'")
    
    print(f"\n✅ Testearemos con: '{titulo}'\n")
    
    # Crear scraper
    scraper = SeleniumScraper()
    
    # Preguntar qué portal probar
    print("¿Cuál portal quieres probar?")
    print("1️⃣  Indeed")
    print("2️⃣  InfoJobs")
    print("3️⃣  Computrabajo")
    print("4️⃣  Todos\n")
    
    opcion = input("Tu opción (1-4): ").strip()
    
    resultados = {}
    
    if opcion in ["1", "4"]:
        resultados["Indeed"] = scraper.test_indeed(titulo)
    
    if opcion in ["2", "4"]:
        resultados["InfoJobs"] = scraper.test_infojobs(titulo)
    
    if opcion in ["3", "4"]:
        resultados["Computrabajo"] = scraper.test_computrabajo(titulo)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70 + "\n")
    
    for portal, resultado in resultados.items():
        estado = "✅ FUNCIONA" if resultado else "❌ PROBLEMA"
        print(f"{portal:20} {estado}")
    
    print("\n" + "="*70)
    print("📁 Archivos generados:")
    print("   • Screenshots: indeed_screenshot_*.png, etc.")
    print("   • HTML: debug_indeed.html, debug_infojobs.html, etc.")
    print("="*70 + "\n")
    
    # Si funcionó, dar siguiente paso
    if any(resultados.values()):
        print("✅ ¡El scraping SÍ funciona!")
        print("Próximos pasos:")
        print("  1. Los selectores están funcionando")
        print("  2. Podemos usar estos datos en el programa principal")
        print("  3. Usa Selenium en lugar de requests\n")
    else:
        print("❌ Ningún portal funcionó")
        print("Intenta:")
        print("  1. Conectarte a Internet")
        print("  2. Verifica que los portales estén activos")
        print("  3. Revisa los screenshots generados\n")