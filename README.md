# job_monitor_whatsapp

PASO 1: Instalar dependencias
bashpip install requests beautifulsoup4 schedule twilio
PASO 2: Configurar Twilio (para WhatsApp)

Ve a https://www.twilio.com
Crea cuenta gratuita (te dan $15 de crédito)
Obtén tu Account SID y Auth Token en el dashboard
Activa Twilio Sandbox para WhatsApp
Sigue las instrucciones para vincular tu número

PASO 3: Configurar el programa
Edita estas líneas en el código:
pythonTWILIO_ACCOUNT_SID = "tu_account_sid_aqui"
TWILIO_AUTH_TOKEN = "tu_auth_token_aqui"
TU_NUMERO_WHATSAPP = "whatsapp:+34XXXXXXXXX"  # Tu número
PASO 4: Ejecutar
bashpython job_monitor.py
```

---

## ⚙️ QUÉ HACE EL PROGRAMA:

✅ **Busca en múltiples portales:**
- Indeed
- InfoJobs
- LinkedIn (con configuración adicional)

✅ **Evita duplicados:** Guarda ofertas en BD local

✅ **Envía por WhatsApp:**
- Cada oferta nueva al instante
- Resumen diario a las 9:00 AM

✅ **Se ejecuta automáticamente:**
- Cada 2 horas
- En background

✅ **Registro de actividad:**
- Log de búsquedas
- Errores y problemas

---

## 📱 EJEMPLO DE MENSAJE EN WHATSAPP:
```
🎯 NUEVA OFERTA ENCONTRADA

📌 Backend Developer Java
🏢 Capgemini
💼 Portal: INDEED
💰 Salario: €26.000-30.000

🔗 https://indeed.com/viewjob?jk=xxxxx

⏰ Encontrada: 27/10/2025 14:32

💡 OPCIONES DE EJECUCIÓN:

Una sola búsqueda: Verifica portales una vez
Automático: Se ejecuta cada 2 horas indefinidamente
En servidor: Puedes dejarlo corriendo 24/7 en un VPS


🔧 CONFIGURACIÓN AVANZADA:
Si quieres cambiar:

Frecuencia: Busca schedule.every(2).hours y cambia 2
Hora del resumen: Busca schedule.every().day.at("09:00")
Palabras clave: Edita "keywords" en cada portal


⚠️ IMPORTANTE:

Twilio gratis: Solo funciona durante fase de testing (necesitas verificar tu número)
API limitadas: Algunos portales pueden tener rate limits
Mejor alternativa para produción: Usar VPS con este script (DigitalOcean, Heroku)
