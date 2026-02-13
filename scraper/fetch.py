import os
import time
import logging
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    logging.info("🔌 Conectando al Chrome Zombie (Puerto 9222)...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def wait_for_human_unlock(driver):
    """
    Bucle infinito que espera hasta que el usuario resuelva el CAPTCHA.
    Detecta el desbloqueo cuando desaparece el texto de bloqueo.
    """
    print("\n" + "🚨"*20)
    print("BLOQUEO DETECTADO: Resuelve el CAPTCHA en Chrome.")
    print("El script continuará AUTOMÁTICAMENTE cuando termines.")
    print("🚨"*20 + "\n")

    while True:
        try:
            html = driver.page_source.lower()
            # Si ya no hay bloqueo, salimos del bucle
            if "uso indebido" not in html and "captcha" not in html:
                print("✅ Desbloqueo detectado. Continuando...")
                time.sleep(2) # Espera de seguridad
                return True
            
            # Si sigue bloqueado, esperamos 1 segundo y volvemos a mirar
            time.sleep(1)
        except:
            return False

def load_or_fetch_page(url):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    filepath = os.path.join("cached_pages", f"page_{url_hash}.html")

    if not os.path.exists("cached_pages"):
        os.makedirs("cached_pages")

    if os.path.exists(filepath):
        logging.info(f"Caché: ...{url_hash[-10:]}.html")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    logging.info(f"Navegando: {url}")
    try:
        driver = get_driver()
        driver.get(url)
        time.sleep(3) 
        
        # --- LÓGICA AUTO-DESBLOQUEO ---
        if "uso indebido" in driver.page_source or "captcha" in driver.page_source.lower():
            wait_for_human_unlock(driver)
        # ------------------------------

        html = driver.page_source
        # Doble chequeo final
        if "uso indebido" not in html:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            return html
        return None
    except Exception as e:
        logging.error(f"Error fetch: {e}")
        return None
