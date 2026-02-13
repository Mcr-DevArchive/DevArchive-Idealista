# CLI + orquestación.
import argparse
import csv
import json
import logging
import time
import os
import shutil
import subprocess
import socket
from random import randint
from . import fetch, parse, notify, history  # <--- Importamos history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def random_sleep(min_s=2, max_s=10):
    time.sleep(randint(min_s, max_s))

def check_port_open(host="127.0.0.1", port=9222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def setup_chrome_zombie():
    if check_port_open():
        logging.info("✅ Chrome Zombie detectado (Puerto 9222 abierto).")
        return True

    print("⚠️  Iniciando Chrome en modo control remoto...")
    os.system("taskkill /F /IM chrome.exe >nul 2>&1")
    time.sleep(1)

    profile = r"C:\selenium\ChromeProfile"
    os.makedirs(profile, exist_ok=True)
    
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        chrome = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    subprocess.Popen([chrome, "--remote-debugging-port=9222", f"--user-data-dir={profile}"])
    time.sleep(4)
    return True

def get_url_for_page(base_url, page):
    if "?" in base_url:
        path, params = base_url.split("?", 1)
        suffix = f"?{params}"
    else:
        path, suffix = base_url, ""

    clean = path.split("/pagina-")[0]
    if clean.endswith(".htm"): clean = clean[:-4]
    if clean.endswith("/"): clean = clean[:-1]
        
    return f"{clean}/pagina-{page}.htm{suffix}"

def save_csv(data, path):
    if not data: return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def save_json(data, path):
    if not data: return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def process_and_notify(properties, auto_send):
    """
    Filtra los pisos nuevos y envía notificaciones.
    """
    if not properties:
        logging.info("No se encontraron propiedades en el escaneo.")
        return

    # 1. FILTRAR: Solo queremos los nuevos
    new_properties, updated_history = history.filter_new_properties(properties)
    
    count_new = len(new_properties)
    logging.info(f"🔎 Análisis: {len(properties)} encontrados | ✨ {count_new} NUEVOS.")

    if count_new == 0:
        logging.info("💤 Nada nuevo que reportar.")
        return

    # 2. DECIDIR SI ENVIAR
    should_send = auto_send
    if not should_send:
        # Modo interactivo solo si no estamos en modo automático
        print(f"\n¡Se han encontrado {count_new} pisos NUEVOS!")
        resp = input("¿Quieres enviarlos a Telegram? (s/n): ").lower()
        if resp == 's':
            should_send = True

    # 3. ENVIAR Y GUARDAR
    if should_send:
        if not notify.check_credentials():
            logging.error("❌ No hay credenciales .env configuradas.")
            return

        logging.info(f"📨 Enviando {count_new} alertas a Telegram...")
        
        for i, item in enumerate(new_properties):
            msg = (
                f"✨ <b>NUEVO: {item.get('price','–')}</b>\n"
                f"📍 {item.get('location','–')}\n"
                f"📏 {item.get('size_m2','–')}m² | 🛏️ {item.get('rooms','–')}\n"
                f"🔗 {item.get('link','–')}"
            )
            notify.send_message(msg)
            # Pequeña pausa para no saturar la API de Telegram
            time.sleep(2) 
        
        logging.info("✅ Enviados correctamente.")
        
        # SOLO guardamos en el historial si hemos enviado el aviso
        # Así si falla el envío, nos avisará la próxima vez
        history.save_history(updated_history)
        logging.info("💾 Historial actualizado.")
    else:
        logging.info("Omitiendo envío a Telegram.")

def run_scraper_cycle(base_url, pages, auto_send, clean):
    """Ejecuta una vuelta completa del scraper"""
    if not os.path.exists("cached_pages"): os.makedirs("cached_pages", exist_ok=True)
    
    all_properties = []
    
    # Scrapeo de páginas
    for num in pages:
        target = get_url_for_page(base_url, num)
        try:
            html = fetch.load_or_fetch_page(target)
            if html:
                datos = parse.extract_data(parse.parse_html(html))
                if datos: all_properties.extend(datos)
                logging.info(f"Página {num}: {len(datos) if datos else 0} pisos.")
            
            if num != pages[-1]: random_sleep()
        except Exception as e:
            logging.error(f"Fallo pág {num}: {e}")

    # Guardar raw data (opcional, sobrescribe el anterior)
    save_csv(all_properties, "properties.csv")
    
    # Procesar lógica de negocio (filtrado y envío)
    process_and_notify(all_properties, auto_send)

    if clean:
        shutil.rmtree("cached_pages", ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Scraper Idealista Pro")
    parser.add_argument("--url", type=str, help="URL de búsqueda")
    parser.add_argument("--pages", nargs="+", type=int, default=[1], help="Páginas a escanear")
    parser.add_argument("--send-telegram", action="store_true", help="Auto-enviar sin preguntar")
    parser.add_argument("--clean", action="store_true", help="Borrar caché tras cada ciclo")
    parser.add_argument("--loop", type=int, default=0, help="Minutos de espera para bucle infinito (0 = una sola vez)")
    
    args = parser.parse_args()

    # 1. Configurar navegador
    setup_chrome_zombie()

    # 2. Obtener URL
    base_url = args.url
    if not base_url:
        print("\n⏳ Esperando URL...")
        base_url = input("👉 Pega la URL de Idealista: ").strip()

    # 3. Ejecución
    if args.loop > 0:
        logging.info(f"🔄 MODO BUCLE ACTIVADO: Escaneando cada {args.loop} minutos.")
        while True:
            logging.info("▶️ Iniciando ciclo de escaneo...")
            run_scraper_cycle(base_url, args.pages, args.send_telegram, args.clean)
            
            logging.info(f"⏸️ Ciclo terminado. Esperando {args.loop} minutos...")
            time.sleep(args.loop * 60)
    else:
        # Ejecución única
        run_scraper_cycle(base_url, args.pages, args.send_telegram, args.clean)

if __name__ == "__main__":
    main()
