import os
import time
import logging
import hashlib
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def get_driver():
    options = Options()
    
    # IMPORTANTE: Desactivar --headless para que puedas ver el navegador y resolver el captcha
    # options.add_argument("--headless") 
    
    # Truco 1: Usar un User-Agent real de Windows 10
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    options.set_preference("general.useragent.override", user_agent)
    
    # Truco 2: Desactivar flags que delatan a la automatización
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def load_or_fetch_page(url):
    # Generamos un hash corto para el nombre del archivo (Solución al error de ruta larga)
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    filename = f"page_{url_hash}.html"
    folder = "cached_pages"
    filepath = os.path.join(folder, filename)

    if not os.path.exists(folder):
        os.makedirs(folder)

    # 1. Comprobar caché
    if os.path.exists(filepath):
        logging.info(f"Caché encontrada: {filename}")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    # 2. Descargar si no existe
    logging.info(f"Descargando URL: {url} ...")
    driver = None
    try:
        driver = get_driver()
        driver.get(url)
        
        # Espera inicial para carga
        time.sleep(3) 
        
        # --- LÓGICA DE DETECCIÓN DE CAPTCHA ---
        page_source = driver.page_source.lower()
        
        # Palabras clave que indican que Idealista te ha bloqueado
        if "verificación" in page_source or "captcha" in page_source or "peticiones tuyas" in page_source:
            print("\n" + "!"*50)
            print("⚠️  BLOQUEO DETECTADO: Idealista pide verificación.")
            print("👉 POR FAVOR: Ve a la ventana de Firefox abierta.")
            print("👉 Resuelve el CAPTCHA o haz clic en 'No soy un robot'.")
            print("👉 Asegúrate de que puedes ver el listado de pisos.")
            input("✅ Cuando ya veas los pisos en el navegador, PULSA ENTER AQUÍ para continuar...")
            print("!"*50 + "\n")
            
            # Recargamos el HTML después de que el usuario haya resuelto el problema
            time.sleep(2)
        # ---------------------------------------

        html = driver.page_source
        
        # Verificación final de seguridad antes de guardar basura
        if "peticiones tuyas" in html.lower():
             logging.error("Parece que el bloqueo persiste. No se guardará esta página.")
             return None

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
            
        logging.info(f"Guardado en caché: {filename}")
        return html

    except Exception as e:
        logging.error(f"Error descargando {url}: {e}")
        return None
    finally:
        if driver:
            driver.quit()
