import json
import os
import logging

HISTORY_FILE = "history.json"

def load_history():
    """Carga los IDs (links) de los pisos ya enviados."""
    if not os.path.exists(HISTORY_FILE):
        return set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        logging.error(f"Error cargando historial: {e}")
        return set()

def save_history(sent_links_set):
    """Guarda los IDs actualizados."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            # Convertimos set a list para que sea serializable en JSON
            json.dump(list(sent_links_set), f, indent=2)
    except Exception as e:
        logging.error(f"Error guardando historial: {e}")

def filter_new_properties(properties):
    """
    Recibe una lista de diccionarios (pisos).
    Devuelve:
      1. Lista de pisos NUEVOS (que no estaban en el historial).
      2. El set de historial actualizado.
    """
    history = load_history()
    new_items = []

    for p in properties:
        link = p.get('link')
        if not link:
            continue
        
        # Usamos el link como ID único
        if link not in history:
            new_items.append(p)
            history.add(link)
    
    return new_items, history
