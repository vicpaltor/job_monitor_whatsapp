"""
JOB MONITOR - Sistema de monitoreo de portales de empleo
Envía ofertas directamente a WhatsApp cada vez que encuentra coincidencias
Autor: Tu nombre
Fecha: 2025
"""

import requests
import json
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
import schedule
import time
import os
from urllib.parse import urlencode

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

class JobMonitorConfig:
    """Configuración centralizada del programa"""
    
    # API de Twilio para WhatsApp (necesitas crear cuenta)
    TWILIO_ACCOUNT_SID = "tu_account_sid_aqui"
    TWILIO_AUTH_TOKEN = "tu_auth_token_aqui"
    TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155552671"  # Número de Twilio
    TU_NUMERO_WHATSAPP = "whatsapp:+34XXXXXXXXX"  # Tu número con +34 para España
    
    # Base de datos
    DB_NAME = "job_monitor.db"
    
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
    
    # Portales a monitorear
    PORTALES = {
        "linkedin": {
            "url": "https://www.linkedin.com/jobs/search/",
            "parametros": {"keywords": "backend remote spain"}
        },
        "indeed": {
            "url": "https://es.indeed.com/jobs",
            "parametros": {"q": "backend remote", "l": "Spain"}
        },
        "infojobs": {
            "url": "https://www.infojobs.net/search",
            "parametros": {"q": "backend remoto"}
        },
        "stackoverflow": {
            "url": "https://stackoverflow.com/jobs/feed",
            "parametros": {"q": "backend", "l": "remote"}
        }
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
                fecha_encontrada TIMESTAMP,
                enviada_whatsapp INTEGER DEFAULT 0
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
    
    def marcar_como_enviada(self, oferta_id):
        """Marca oferta como enviada por WhatsApp"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ofertas SET enviada_whatsapp = 1 WHERE id = ?",
            (oferta_id,)
        )
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
    
    def buscar_en_linkedin(self):
        """Busca ofertas en LinkedIn"""
        print("🔍 Buscando en LinkedIn...")
        ofertas = []
        
        try:
            url = JobMonitorConfig.PORTALES["linkedin"]["url"]
            parametros = {
                "keywords": "backend developer remote spain",
                "salary": "80000-120000",
                "f_WT": "2"  # Remote
            }
            
            # Nota: LinkedIn requiere autenticación. Alternativa: usar API no oficial
            # Esta es una implementación básica que necesitarías adaptar
            
            self.db.agregar_log(
                "linkedin", 
                "busqueda", 
                "Búsqueda completada (requiere autenticación para resultados completos)"
            )
            
        except Exception as e:
            print(f"❌ Error en LinkedIn: {e}")
            self.db.agregar_log("linkedin", "error", str(e))
        
        return ofertas
    
    def buscar_en_indeed(self):
        """Busca ofertas en Indeed"""
        print("🔍 Buscando en Indeed...")
        ofertas = []
        
        try:
            url = "https://es.indeed.com/jobs"
            parametros = {
                "q": "backend developer remote",
                "l": "Spain",
                "radius": "0",
                "jt": "fulltime",
                "salary": "25000-32000"
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
                        titulo = job.find("h2").text.strip()
                        empresa = job.find("span", class_="companyName").text.strip()
                        url_job = job.find("a", class_="jcs-JobTitle")["href"]
                        salario_text = job.find("span", class_="salary-snippet")
                        
                        oferta = {
                            "id": f"indeed_{titulo}_{empresa}",
                            "titulo": titulo,
                            "empresa": empresa,
                            "url": f"https://indeed.com{url_job}",
                            "salario": salario_text.text if salario_text else "No especificado",
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
                "q": "backend remoto",
                "l": "Spain"
            }
            
            response = requests.get(
                url,
                params=parametros,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                jobs = soup.find_all("div", class_="offer")
                
                for job in jobs[:10]:
                    try:
                        titulo = job.find("h2", class_="title").text.strip()
                        empresa = job.find("span", class_="company").text.strip()
                        url_job = job.find("a")["href"]
                        
                        oferta = {
                            "id": f"infojobs_{titulo}_{empresa}",
                            "titulo": titulo,
                            "empresa": empresa,
                            "url": f"https://infojobs.net{url_job}",
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
        
        except Exception as e:
            print(f"❌ Error en InfoJobs: {e}")
            self.db.agregar_log("infojobs", "error", str(e))
        
        return ofertas
    
    def obtener_todas_las_ofertas(self):
        """Ejecuta búsqueda en todos los portales"""
        todas_ofertas = []
        
        todas_ofertas.extend(self.buscar_en_indeed())
        todas_ofertas.extend(self.buscar_en_infojobs())
        # todas_ofertas.extend(self.buscar_en_linkedin())  # Requiere configuración especial
        
        return todas_ofertas


# ============================================================================
# GESTOR DE WHATSAPP
# ============================================================================

class WhatsAppManager:
    """Gestiona envío de mensajes por WhatsApp via Twilio"""
    
    def __init__(self):
        self.account_sid = JobMonitorConfig.TWILIO_ACCOUNT_SID
        self.auth_token = JobMonitorConfig.TWILIO_AUTH_TOKEN
        self.from_number = JobMonitorConfig.TWILIO_WHATSAPP_NUMBER
        self.to_number = JobMonitorConfig.TU_NUMERO_WHATSAPP
    
    def enviar_oferta(self, oferta):
        """Envía una oferta por WhatsApp"""
        
        mensaje = self._formatear_mensaje(oferta)
        
        try:
            # URL de API de Twilio
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            
            datos = {
                "From": self.from_number,
                "To": self.to_number,
                "Body": mensaje
            }
            
            response = requests.post(
                url,
                data=datos,
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Oferta enviada: {oferta['titulo']}")
                return True
            else:
                print(f"❌ Error enviando: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Error de conexión Twilio: {e}")
            return False
    
    def _formatear_mensaje(self, oferta):
        """Formatea la oferta para WhatsApp"""
        
        mensaje = f"""
🎯 NUEVA OFERTA ENCONTRADA

📌 {oferta['titulo']}
🏢 {oferta['empresa']}
💼 Portal: {oferta['portal'].upper()}
💰 Salario: {oferta['salario']}

🔗 {oferta['url']}

⏰ Encontrada: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        return mensaje.strip()
    
    def enviar_resumen_diario(self, ofertas_nuevas):
        """Envía resumen diario de ofertas"""
        
        if not ofertas_nuevas:
            resumen = "📊 RESUMEN DIARIO\n\nNo hay nuevas ofertas hoy. ❌"
        else:
            resumen = f"""
📊 RESUMEN DIARIO

✅ Se encontraron {len(ofertas_nuevas)} ofertas nuevas:

"""
            for oferta in ofertas_nuevas[:5]:  # Máximo 5 en resumen
                resumen += f"• {oferta['titulo']} - {oferta['empresa']}\n"
            
            if len(ofertas_nuevas) > 5:
                resumen += f"\n... y {len(ofertas_nuevas) - 5} más"
        
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            datos = {
                "From": self.from_number,
                "To": self.to_number,
                "Body": resumen
            }
            
            requests.post(url, data=datos, auth=(self.account_sid, self.auth_token))
            print("✅ Resumen diario enviado")
        
        except Exception as e:
            print(f"❌ Error enviando resumen: {e}")


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

class JobMonitor:
    """Coordina el monitoreo completo"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = PortalScraper()
        self.whatsapp = WhatsAppManager()
    
    def ejecutar_monitoreo(self):
        """Ejecuta una ronda completa de monitoreo"""
        
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO MONITOREO: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Obtener ofertas de todos los portales
        todas_ofertas = self.scraper.obtener_todas_las_ofertas()
        print(f"\n📊 Total de ofertas encontradas: {len(todas_ofertas)}")
        
        ofertas_nuevas = []
        
        # Procesar cada oferta
        for oferta in todas_ofertas:
            if not self.db.oferta_existe(oferta["id"]):
                # Oferta nueva - guardar y enviar
                self.db.guardar_oferta(oferta)
                self.whatsapp.enviar_oferta(oferta)
                self.db.marcar_como_enviada(oferta["id"])
                ofertas_nuevas.append(oferta)
            else:
                print(f"⏭️  Oferta duplicada: {oferta['titulo']}")
        
        # Enviar resumen
        if ofertas_nuevas:
            print(f"\n✅ {len(ofertas_nuevas)} ofertas nuevas encontradas")
        else:
            print("\n⏭️  No hay ofertas nuevas en este monitoreo")
        
        print(f"\n{'='*60}\n")
    
    def programar(self):
        """Programa el monitoreo automático"""
        
        print("📅 Programando monitoreo automático...\n")
        
        # Monitorear cada 2 horas
        schedule.every(2).hours.do(self.ejecutar_monitoreo)
        
        # Resumen diario a las 9:00 AM
        schedule.every().day.at("09:00").do(self.enviar_resumen_diario)
        
        print("✅ Programación completada")
        print("⏰ Monitoreo cada 2 horas")
        print("📊 Resumen diario a las 09:00 AM\n")
        
        # Mantener el programa corriendo
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    
    def enviar_resumen_diario(self):
        """Obtiene ofertas del día y envía resumen"""
        # Aquí iría lógica para obtener ofertas del día
        self.whatsapp.enviar_resumen_diario([])


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     JOB MONITOR - Backend Remote      ║
    ║  Sistema de Monitoreo a WhatsApp      ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("⚙️  Inicializando...\n")
    
    monitor = JobMonitor()
    
    # Opción 1: Ejecutar una sola vez
    print("Selecciona una opción:")
    print("1. Ejecutar monitoreo ahora (una sola vez)")
    print("2. Programar monitoreo automático")
    print("3. Salir\n")
    
    opcion = input("Tu opción (1-3): ").strip()
    
    if opcion == "1":
        monitor.ejecutar_monitoreo()
    elif opcion == "2":
        monitor.programar()
    else:
        print("👋 Saliendo...")
