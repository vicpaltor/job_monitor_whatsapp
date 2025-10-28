# job_monitor_whatsapp

Perfecto, ahora el programa sin costo alguno. Guarda todo en archivos TXT.
🚀 INSTALACIÓN:
bashpip install requests beautifulsoup4 schedule
📝 CÓMO FUNCIONA:
El programa crea 3 archivos automáticamente:

ofertas_nuevas.txt - Cada oferta nueva aparece aquí al instante
resumen_diario.txt - Resumen de todas las ofertas del día (a las 21:00)
job_monitor.db - Base de datos interna (evita duplicados)

▶️ EJECUCIÓN:
bashpython job_monitor.py
```

Luego elige:
- **Opción 1:** Una búsqueda rápida
- **Opción 2:** Monitoreo 24/7 (cada 2 horas automático)

## 📄 EJEMPLO DE SALIDA EN TXT:
```
======================================================================
🎯 NUEVA OFERTA ENCONTRADA
======================================================================
📌 Título: Backend Developer Java
🏢 Empresa: Capgemini
💼 Portal: INDEED
💰 Salario: €26.000-30.000
🔗 URL: https://es.indeed.com/viewjob?jk=xxxxx
⏰ Encontrada: 27/10/2025 14:32:45
======================================================================
⚡ CARACTERÍSTICAS:
✅ Sin costos - Solo usa librerías gratis
✅ Sin API keys - No necesita configuración
✅ Evita duplicados - BD local controla ofertas vistas
✅ 3 portales - Indeed, InfoJobs, Computrabajo
✅ Automático 24/7 - Se ejecuta solo cada 2 horas
✅ Resumen diario - A las 21:00 cada día


🧪 CÓMO USARLO:
bashpython job_monitor_debug.py
```

Te pedirá:
```
Ingresa el título a buscar (ej: 'backend remote'): backend remote
¿Cuál portal quieres probar?
1️⃣  Indeed
2️⃣  InfoJobs
3️⃣  Computrabajo
4️⃣  Todos
```

## 📊 QUÉ HACE:

✅ Prueba cada portal individualmente
✅ Muestra el status code HTTP (200, 403, 429, etc.)
✅ Intenta 5 selectores CSS diferentes por portal
✅ Te dice exactamente cuántas ofertas encontró (o 0)
✅ **Guarda el HTML en archivos** para que veas qué está pasando:
  - `debug_indeed.html`
  - `debug_infojobs.html`
  - `debug_computrabajo.html`

## 📋 EJEMPLO DE SALIDA:
```
🧪 PROBANDO INDEED
======================================================================

📍 URL base: https://es.indeed.com/jobs
🔍 Parámetros:
   • q: backend remote
   • l: Spain
   • radius: 0
   • jt: fulltime

📤 Enviando petición...

📥 Respuesta recibida:
   • Status Code: 200
   • Tamaño: 45230 bytes

🔎 Buscando ofertas con diferentes selectores:

   • Selector 1 (job_seen_beacon): 12 resultados ✅
   • Selector 2 (job-tile): 0 resultados
   • Selector 3 (article): 45 resultados

🔍 INTERPRETACIÓN DE RESULTADOS:
Status Code 200 = ✅ Conexión OK
Status Code 403 = ❌ Bloqueado (debes cambiar headers)
Status Code 429 = ⚠️ Too many requests (esperar)
Si encuentra 0 ofertas en todos los selectores:

Abre el archivo debug_indeed.html
Verás qué HTML devolvió Indeed
Si dice "Enable JavaScript" = Indeed requiere JS

Si encuentra ofertas (ej: 12 resultados):

✅ El scraping funciona
✅ Solo necesito actualizar los selectores CSS
