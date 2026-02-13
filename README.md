# 🏠 Idealista Scraper

Un scraper modular en Python para Idealista, con notificación opcional por Telegram. 

## 🧟 Modo Anti-Bloqueo (Zombie Mode)

Para evitar que Idealista detecte el bot y bloquee tu IP, este script utiliza una técnica avanzada: **se conecta a una sesión de Chrome real** en lugar de abrir una nueva.

### ¿Cómo funciona?
1. El script cerrará automáticamente tus ventanas de Chrome abiertas.
2. Abrirá una nueva ventana de Chrome en "modo depuración" (Puerto 9222).
3. **Creará una carpeta de perfil** en `C:\selenium\ChromeProfile`.

### ¿Por qué crea esta carpeta?
- **Persistencia de Sesión:** Al usar un perfil guardado en `C:\selenium`, Chrome recuerda tus cookies y datos de navegación.
- **Evita Captchas:** Si ya has resuelto un captcha una vez, Idealista te recordará y no te lo pedirá de nuevo en cada ejecución.
- **Huella Digital Humana:** Hace que el navegador parezca 100% legítimo, evitando baneos por comportamiento robótico.

> **Nota:** Puedes borrar la carpeta `C:\selenium` en cualquier momento si quieres reiniciar la "memoria" del navegador, pero tendrás que resolver los captchas de nuevo.

## 🚀 Características
- Usa Selenium + BeautifulSoup para scrapear datos de inmuebles.
- Cachea las páginas localmente para evitar sobrecargar el sitio.
- Guarda resultados en CSV.
- Envía los datos a un chat de Telegram opcionalmente.

## 🛠 Requisitos
- Python 3.8+
- Firefox instalado

## ⚙ Instalación
```bash
pip install -r requirements.txt
```

🔧 Configuración

Crea un archivo .env en el raíz con:

```
TELEGRAM_TOKEN=<tu_token_aqui>
TELEGRAM_CHAT_ID=<tu_chat_id_aqui>
CACHE_DIR=./cached_pages
```
🚀 Uso
El script funciona conectándose a una ventana de Chrome ya abierta (para evitar bloqueos).

1. Ejecución Básica (Escaneo único)
```
python -m scraper.main --url "TU_URL_DE_IDEALISTA" --send-telegram
```
Si no pasas la --url, el script te la pedirá de forma interactiva.

2. Modo Vigilancia (Bucle Infinito)
Escanea cada 30 minutos y avisa solo de los pisos nuevos.

```
python -m scraper.main --url "..." --pages 1 2 --send-telegram --loop 30
```

Argumentos Disponibles
- `--url "..."`: La URL de búsqueda de Idealista (con tus filtros).
- `--pages 1 2 3`: Qué páginas escanear (por defecto solo la 1).
- `--send-telegram`: Activa el envío de alertas.
- `--loop X`: Repite el proceso cada X minutos.
- `--clean`: Borra la caché de archivos HTML al terminar.

📂 Estructura del Proyecto

- `scraper/main.py` → CLI Principal: Orquestación, bucles y argumentos.
- `scraper/fetch.py` → Motor de Descarga: Gestiona Selenium y el bypass de Captcha.
- `scraper/parse.py` → Parser: Extrae datos limpios con BeautifulSoup.
- `scraper/notify.py` → Notificaciones: Envía mensajes a Telegram usando .env.
- `scraper/history.py` → Memoria: Gestiona history.json para evitar duplicados.

