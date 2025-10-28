"""
JOB MONITOR - VERSIÓN DEBUG
Prueba de scraping con información detallada
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ============================================================================
# HERRAMIENTAS DE DEBUG
# ============================================================================

class DebugScraper:
    """Scraper con información detallada para debugging"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def test_indeed(self, titulo_busqueda):
        """Prueba Indeed con información detallada"""
        print("\n" + "="*70)
        print(f"🧪 PROBANDO INDEED")
        print("="*70 + "\n")
        
        try:
            url = "https://es.indeed.com/jobs"
            parametros = {
                "q": titulo_busqueda,
                "l": "Spain",
                "radius": "0",
                "jt": "fulltime"
            }
            
            print(f"📍 URL base: {url}")
            print(f"🔍 Parámetros:")
            for key, value in parametros.items():
                print(f"   • {key}: {value}")
            
            print(f"\n📤 Enviando petición...\n")
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            print(f"📥 Respuesta recibida:")
            print(f"   • Status Code: {response.status_code}")
            print(f"   • Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   • Tamaño: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Buscar diferentes selectores
                print(f"\n🔎 Buscando ofertas con diferentes selectores:\n")
                
                # Selector 1
                jobs1 = soup.find_all("div", class_="job_seen_beacon")
                print(f"   • Selector 1 (job_seen_beacon): {len(jobs1)} resultados")
                
                # Selector 2
                jobs2 = soup.find_all("div", class_="job-tile")
                print(f"   • Selector 2 (job-tile): {len(jobs2)} resultados")
                
                # Selector 3
                jobs3 = soup.find_all("article")
                print(f"   • Selector 3 (article): {len(jobs3)} resultados")
                
                # Selector 4
                jobs4 = soup.find_all("li", class_="css-5lfssm")
                print(f"   • Selector 4 (li css-5lfssm): {len(jobs4)} resultados")
                
                # Buscar todos los divs con clase que contenga "job"
                jobs_all = soup.find_all("div", class_=lambda x: x and "job" in x.lower())
                print(f"   • Selector genérico (contiene 'job'): {len(jobs_all)} resultados")
                
                # Guardar HTML para inspección
                with open("debug_indeed.html", "w", encoding="utf-8") as f:
                    f.write(response.text[:5000])  # Primeros 5000 caracteres
                print(f"\n📄 HTML guardado en: debug_indeed.html")
                
                # Mostrar estructura básica
                print(f"\n🏗️ Estructura de la página:")
                title = soup.find("title")
                print(f"   • Título: {title.text if title else 'N/A'}")
                
                h1 = soup.find("h1")
                print(f"   • H1: {h1.text if h1 else 'N/A'}")
                
                # Verificar si hay errores/bloques
                if "Please enable javascript" in response.text or "Enable JavaScript" in response.text:
                    print(f"\n⚠️ PROBLEMA: Indeed requiere JavaScript")
                    print(f"   Solución: Usar Selenium o API alternativa")
                    return False
                
                if response.status_code == 403:
                    print(f"\n⚠️ PROBLEMA: Acceso denegado (403)")
                    print(f"   Solución: Indeed bloquea este User-Agent")
                    return False
                
                if len(jobs1) == 0 and len(jobs2) == 0 and len(jobs3) == 0:
                    print(f"\n⚠️ PROBLEMA: No se encontraron ofertas")
                    print(f"   Posibles causas:")
                    print(f"   1. Los selectores CSS han cambiado")
                    print(f"   2. Indeed bloqueó la petición")
                    print(f"   3. No hay ofertas para esta búsqueda")
                    return False
                
                return True
            
            else:
                print(f"\n❌ Error HTTP: {response.status_code}")
                if response.status_code == 403:
                    print("   Solución: Aumentar delay o cambiar headers")
                elif response.status_code == 429:
                    print("   Solución: Too many requests, esperar más tiempo")
                return False
        
        except requests.exceptions.Timeout:
            print(f"❌ ERROR: Timeout (conexión muy lenta)")
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    def test_infojobs(self, titulo_busqueda):
        """Prueba InfoJobs con información detallada"""
        print("\n" + "="*70)
        print(f"🧪 PROBANDO INFOJOBS")
        print("="*70 + "\n")
        
        try:
            url = "https://www.infojobs.net/search"
            parametros = {
                "q": titulo_busqueda,
                "c": "47"
            }
            
            print(f"📍 URL base: {url}")
            print(f"🔍 Parámetros:")
            for key, value in parametros.items():
                print(f"   • {key}: {value}")
            
            print(f"\n📤 Enviando petición...\n")
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            print(f"📥 Respuesta recibida:")
            print(f"   • Status Code: {response.status_code}")
            print(f"   • Tamaño: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                print(f"\n🔎 Buscando ofertas:\n")
                
                # Selector 1
                jobs1 = soup.find_all("article", class_="offer")
                print(f"   • Selector 1 (article.offer): {len(jobs1)} resultados")
                
                # Selector 2
                jobs2 = soup.find_all("div", class_="offer")
                print(f"   • Selector 2 (div.offer): {len(jobs2)} resultados")
                
                # Selector 3
                jobs3 = soup.find_all("article")
                print(f"   • Selector 3 (article genérico): {len(jobs3)} resultados")
                
                # Guardar HTML
                with open("debug_infojobs.html", "w", encoding="utf-8") as f:
                    f.write(response.text[:5000])
                print(f"\n📄 HTML guardado en: debug_infojobs.html")
                
                if len(jobs1) == 0 and len(jobs2) == 0:
                    print(f"\n⚠️ PROBLEMA: No se encontraron ofertas")
                    return False
                
                return True
            
            else:
                print(f"\n❌ Error HTTP: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    def test_computrabajo(self, titulo_busqueda):
        """Prueba Computrabajo con información detallada"""
        print("\n" + "="*70)
        print(f"🧪 PROBANDO COMPUTRABAJO")
        print("="*70 + "\n")
        
        try:
            url = "https://www.computrabajo.com/search/jobs"
            parametros = {
                "q": titulo_busqueda,
                "location": "Spain"
            }
            
            print(f"📍 URL base: {url}")
            print(f"🔍 Parámetros:")
            for key, value in parametros.items():
                print(f"   • {key}: {value}")
            
            print(f"\n📤 Enviando petición...\n")
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            print(f"📥 Respuesta recibida:")
            print(f"   • Status Code: {response.status_code}")
            print(f"   • Tamaño: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                print(f"\n🔎 Buscando ofertas:\n")
                
                # Selector 1
                jobs1 = soup.find_all("div", class_="offer-item")
                print(f"   • Selector 1 (offer-item): {len(jobs1)} resultados")
                
                # Selector 2
                jobs2 = soup.find_all("div", class_="job")
                print(f"   • Selector 2 (job): {len(jobs2)} resultados")
                
                # Guardar HTML
                with open("debug_computrabajo.html", "w", encoding="utf-8") as f:
                    f.write(response.text[:5000])
                print(f"\n📄 HTML guardado en: debug_computrabajo.html")
                
                if len(jobs1) == 0 and len(jobs2) == 0:
                    print(f"\n⚠️ PROBLEMA: No se encontraron ofertas")
                    return False
                
                return True
            
            else:
                print(f"\n❌ Error HTTP: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║   JOB MONITOR - MODO DEBUG/PRUEBA    ║
    ║  Diagnóstico de scraping             ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("\n⚙️  Inicializando...\n")
    
    # Pedir título de búsqueda
    titulo = input("Ingresa el título a buscar (ej: 'backend remote'): ").strip()
    
    if not titulo:
        titulo = "backend remote java"
        print(f"⚠️  Usando búsqueda por defecto: '{titulo}'")
    
    print(f"\n✅ Testearemos con: '{titulo}'\n")
    
    # Crear debugger
    debugger = DebugScraper()
    
    # Preguntar qué portal probar
    print("¿Cuál portal quieres probar?")
    print("1️⃣  Indeed")
    print("2️⃣  InfoJobs")
    print("3️⃣  Computrabajo")
    print("4️⃣  Todos\n")
    
    opcion = input("Tu opción (1-4): ").strip()
    
    resultados = {}
    
    if opcion in ["1", "4"]:
        resultados["Indeed"] = debugger.test_indeed(titulo)
    
    if opcion in ["2", "4"]:
        resultados["InfoJobs"] = debugger.test_infojobs(titulo)
    
    if opcion in ["3", "4"]:
        resultados["Computrabajo"] = debugger.test_computrabajo(titulo)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70 + "\n")
    
    for portal, resultado in resultados.items():
        estado = "✅ OK" if resultado else "❌ PROBLEMA"
        print(f"{portal:15} {estado}")
    
    print("\n" + "="*70)
    print("ℹ️  Si algún portal tiene PROBLEMA:")
    print("  1. Revisa el archivo debug_[portal].html")
    print("  2. Abre con tu navegador para ver qué muestra")
    print("  3. El HTML guardado contiene los primeros 5000 caracteres")
    print("="*70 + "\n")
    
    # Soluciones
    print("🔧 SOLUCIONES POSIBLES:\n")
    print("Si NINGÚN portal funciona:")
    print("  ❌ Problem: Indeed/InfoJobs pueden estar bloqueando")
    print("  ✅ Solución: Usar Selenium (requiere navegador)")
    print("\nSi funciona al menos UNO:")
    print("  ✅ ¡El scraping SÍ funciona!")
    print("  ✅ Los selectores CSS pueden haber cambiado")
    print("  ✅ Solución: Actualizar selectores en el código\n")