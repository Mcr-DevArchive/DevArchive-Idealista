from bs4 import BeautifulSoup
import logging

def parse_html(html_content):
    """Convierte el HTML en objeto BeautifulSoup"""
    return BeautifulSoup(html_content, "html.parser")

def extract_data(soup):
    """
    Extrae la lista de pisos del objeto BeautifulSoup.
    Devuelve una lista de diccionarios.
    """
    properties = []
    
    # Buscamos todos los artículos que sean anuncios
    # Idealista usa <article class="item ...">
    articles = soup.find_all("article", class_="item")
    
    if not articles:
        # A veces Idealista cambia la clase o bloquea
        return []

    for article in articles:
        try:
            # 1. Ignorar publicidad disfrazada
            if "adv" in article.get("class", []) or "paid" in article.get("class", []):
                continue
            
            # 2. Extracción segura de datos
            item = {}
            
            # --- Link ---
            link_tag = article.find("a", class_="item-link")
            if not link_tag:
                continue # Si no tiene link, no es un piso válido
            item["link"] = "https://www.idealista.com" + link_tag.get("href")
            item["description"] = link_tag.get("title", "Sin título")

            # --- Precio ---
            price_tag = article.find("span", class_="item-price")
            if price_tag:
                item["price"] = price_tag.text.strip()
            else:
                item["price"] = "Consultar"

            # --- Detalles (Habitaciones, m2, planta) ---
            # Idealista suele poner esto en spans dentro de item-detail-char
            details = article.find_all("span", class_="item-detail")
            
            # Valores por defecto
            item["rooms"] = "?"
            item["size_m2"] = "?"
            item["floor"] = "?"

            for det in details:
                text = det.text.strip().lower()
                if "hab" in text or "dorm" in text:
                    item["rooms"] = text
                elif "m²" in text:
                    item["size_m2"] = text
                elif "planta" in text or "bajo" in text:
                    item["floor"] = text

            # --- Localidad / Barrio ---
            # A veces está en el título, a veces en un tag específico
            # Intentamos buscar la zona
            item["location"] = item["description"] # Fallback

            properties.append(item)

        except Exception as e:
            # Si falla un piso concreto, lo ignoramos pero no paramos el script
            # logging.warning(f"Error parseando un anuncio: {e}") # Descomenta para depurar
            continue

    return properties
