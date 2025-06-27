import time
import sqlite3
import requests
import os
import hashlib
from PIL import Image, ImageDraw
import random
import torch
from transformers import pipeline
import io
import sys
import platform
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def log(message):
    """Función para logging con timestamp"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def adaptar_url_mexico(url):
    """Adapta una URL de Booking para forzar el idioma español de México y la moneda en MXN"""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Forzar idioma español de México
    if '.es.' not in parsed.path:
        path_parts = parsed.path.split('.')
        if len(path_parts) > 1:
            path_parts.insert(-1, 'es')
            new_path = '.'.join(path_parts)
            parsed = parsed._replace(path=new_path)
    
    # Forzar moneda a MXN y lenguaje a español de México
    query_params['selected_currency'] = ['MXN']
    query_params['lang'] = ['es-mx']
    
    # Reconstruir URL
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url

def scrape_hotel_full(url):
    """Realiza el scraping completo y detallado de un hotel específico"""
    
    # Configurar geckodriver según el sistema operativo
    sistema = platform.system()
    log(f"Sistema operativo detectado: {sistema}")
    
    if sistema == "Windows":
        gecko_path = "./geckodriver.exe"
    elif sistema == "Linux":
        gecko_path = "./geckodriver"
    else:
        gecko_path = "./geckodriver"
    
    # Configurar opciones de Firefox
    options = Options()
    options.headless = True
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    
    # Inicializar el driver
    service = Service(gecko_path)
    driver = webdriver.Firefox(service=service, options=options)
    
    # Inicializar el clasificador de imágenes para análisis visual
    log("Inicializando clasificador de imágenes para análisis visual...")
    try:
        visual_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
        log("Clasificador visual inicializado correctamente")
    except Exception as e:
        log(f"Error inicializando clasificador visual: {e}")
        visual_classifier = None
    
    # Iniciar cronómetro
    start_time = time.time()
    log(f"Iniciando scraping a las {time.strftime('%H:%M:%S')}")
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 8)
        time.sleep(3)
        log("Página cargada, extrayendo datos...")
        
        def fast_get_text(selector, multiple=False):
            """Función optimizada para extraer texto rápidamente"""
            try:
                if multiple:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    return list({el.text.strip() for el in elements if el.text.strip()})
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
            except Exception:
                return [] if multiple else None
        
        def extract_fast(selectors, multiple=False):
            """Extrae datos usando el primer selector que funcione"""
            for selector in selectors:
                result = fast_get_text(selector, multiple=multiple)
                if result:
                    return result
            return [] if multiple else None
            
        def analyze_image_visually(image_data):
            """Analiza visualmente una imagen para detectar su contenido"""
            if visual_classifier is None:
                return None
            try:
                image = Image.open(io.BytesIO(image_data))
                results = visual_classifier(image)
                pool_keywords = ['swimming pool', 'pool', 'water', 'swimming', 'resort', 'aquatic', 'lagoon', 'pond', 'poolside']
                room_keywords = ['bedroom', 'bed', 'room', 'interior', 'hotel room', 'suite', 'accommodation', 'furniture', 'pillow', 'mattress']
                bathroom_keywords = ['bathroom', 'toilet', 'shower', 'bathtub', 'sink', 'washroom', 'lavatory', 'bath']
                restaurant_keywords = ['restaurant', 'dining', 'food', 'meal', 'cuisine', 'table', 'cafe', 'cafeteria', 'bistro', 'eatery', 'dining room']
                exterior_keywords = ['building', 'exterior', 'architecture', 'facade', 'outdoor', 'structure', 'hotel', 'resort']
                
                for result in results:
                    label = result['label'].lower()
                    confidence = result['score']
                    if confidence > 0.7:
                        if any(keyword in label for keyword in pool_keywords):
                            log(f"Análisis visual detectó: {label} (confianza: {confidence:.2f}) -> PISCINA")
                            return 'piscina'
                        elif any(keyword in label for keyword in room_keywords):
                            log(f"Análisis visual detectó: {label} (confianza: {confidence:.2f}) -> HABITACIÓN")
                            return 'habitacion'
                        elif any(keyword in label for keyword in bathroom_keywords):
                            log(f"Análisis visual detectó: {label} (confianza: {confidence:.2f}) -> BAÑO")
                            return 'baño'
                        elif any(keyword in label for keyword in restaurant_keywords):
                            log(f"Análisis visual detectó: {label} (confianza: {confidence:.2f}) -> RESTAURANTE")
                            return 'restaurante'
                        elif any(keyword in label for keyword in exterior_keywords):
                            log(f"Análisis visual detectó: {label} (confianza: {confidence:.2f}) -> EXTERIOR")
                            return 'exterior'
                return None
            except Exception as e:
                log(f"Error en análisis visual: {e}")
                return None
        
        def classify_image_type(url_img, img_element=None, img_index=None, image_data=None):
            """Clasifica el tipo de imagen usando análisis visual Y palabras clave en URL"""
            if image_data and visual_classifier:
                visual_category = analyze_image_visually(image_data)
                if visual_category:
                    return visual_category
            
            url_lower = url_img.lower()
            room_keywords = ['room', 'bedroom', 'habitacion', 'cuarto', 'suite', 'junior', 'deluxe', 'bed', 'dormitorio', 'doble', 'individual', 'matrimonial']
            exterior_keywords = ['exterior', 'facade', 'fachada', 'building', 'edificio', 'view', 'vista', 'terrace', 'terraza', 'balcon', 'balcony', 'hotel-view', 'outdoor']
            pool_keywords = ['pool', 'piscina', 'swimming', 'natacion', 'agua', 'water', 'swim', 'pileta', 'alberca', 'poolside', 'pool-area', 'poolview', 'aqua', 'splash', 'wet', 'dive', 'float', 'sunbed', 'deck-chair', 'poolbar', 'pool-bar', 'tumbona', 'hamaca', 'solarium']
            bathroom_keywords = ['bathroom', 'baño', 'bath', 'shower', 'ducha', 'wc', 'aseo', 'lavabo', 'toilet']
            restaurant_keywords = ['restaurant', 'restaurante', 'dining', 'comedor', 'bar', 'lobby', 'reception', 'recepcion', 'breakfast', 'buffet', 'cafe']
            
            if any(keyword in url_lower for keyword in pool_keywords):
                return 'piscina'
            elif any(keyword in url_lower for keyword in room_keywords):
                return 'habitacion'
            elif any(keyword in url_lower for keyword in bathroom_keywords):
                return 'baño'
            elif any(keyword in url_lower for keyword in exterior_keywords):
                return 'exterior'
            elif any(keyword in url_lower for keyword in restaurant_keywords):
                return 'restaurante'
            
            if img_index is not None:
                if 8 <= img_index <= 20:
                    no_specific_keywords = (not any(kw in url_lower for kw in room_keywords + bathroom_keywords + restaurant_keywords))
                    if no_specific_keywords:
                        return 'piscina'
            
            if re.search(r'(?:pool|agua|swim|piscina)', url_lower):
                return 'piscina'
            
            pool_number_patterns = ['03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
            url_numbers = re.findall(r'\d{2,}', url_img)
            for num in url_numbers:
                if any(pattern in num for pattern in pool_number_patterns):
                    if not any(kw in url_lower for kw in room_keywords):
                        return 'piscina'
            
            return 'general'
        
        def is_valid_image_url(url):
            """Verifica si la URL es válida para descarga"""
            if not url or 'data:' in url or url.startswith('#'):
                return False
            if url.startswith('//'):
                url = 'https:' + url
            return url.startswith(('http://', 'https://'))

        def download_image(url, hotel_name, img_index, category='general'):
            """Descarga una imagen y la guarda localmente"""
            try:
                if not url or not is_valid_image_url(url):
                    return None
                    
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.jpg'
                    
                    hotel_safe = re.sub(r'[^\w\s-]', '', hotel_name.lower()).strip()
                    hotel_safe = re.sub(r'[-\s]+', '_', hotel_safe)
                    filename = f"hotel_{hash(hotel_name) % 1000}_{img_index}_{category}_{url_hash}{ext}"
                    filepath = os.path.join('imagenes', filename)
                    
                    os.makedirs('imagenes', exist_ok=True)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    return filepath
            except Exception as e:
                log(f"Error descargando imagen {url}: {e}")
                return None

        def select_balanced_images(valid_images, target_count=15):
            """Selecciona imágenes de forma balanceada por categorías usando análisis visual"""
            log("Clasificando imágenes usando análisis visual...")
            
            for i, img in enumerate(valid_images):
                image_data = None
                if visual_classifier:
                    try:
                        response = requests.get(img['url'], timeout=5)
                        if response.status_code == 200:
                            image_data = response.content
                    except Exception as e:
                        log(f"Error descargando imagen para análisis: {e}")
                
                img['category'] = classify_image_type(img['url'], None, i, image_data)
                log(f"Imagen {i}: {img['category']}")
            
            categories = {
                'piscina': [],
                'habitacion': [],
                'baño': [],
                'restaurante': [],
                'exterior': [],
                'general': []
            }
            
            for img in valid_images:
                categories[img['category']].append(img)
            
            selected = []
            selected.extend(categories['piscina'][:4])
            selected.extend(categories['habitacion'][:4])
            selected.extend(categories['baño'][:2])
            selected.extend(categories['restaurante'][:2])
            selected.extend(categories['exterior'][:2])
            selected.extend(categories['general'][:1])
            
            if len(selected) < target_count:
                remaining = target_count - len(selected)
                for cat_name, cat_images in categories.items():
                    for img in cat_images:
                        if img not in selected:
                            selected.append(img)
                            remaining -= 1
                            if remaining == 0:
                                break
                    if remaining == 0:
                        break
            
            log(f"Seleccionadas {len(selected)} imágenes balanceadas")
            return selected[:target_count]
        
        # Extraer nombre del hotel
        log("Extrayendo nombre del hotel...")
        hotel_name_selectors = [
            'h2[data-testid="title"]', 
            'h1[data-testid="title"]', 
            'h1',
            '.pp-header__title',
            '.hp__hotel-name',
            '.property-title'
        ]
        hotel_name = extract_fast(hotel_name_selectors)
        log(f"Nombre: {hotel_name}")

        # Extraer dirección
        log("Extrayendo dirección...")
        address_selectors = [
            '[data-testid="address"]',
            '.hp_address_subtitle',
            '.address',
            '[data-testid="property-address"]',
            '.pp-header__address',
            '.hp__hotel-address',
            '.bui-card__subtitle',
            'span[data-testid="address"]',
            '.hp-address-text'
        ]
        address = extract_fast(address_selectors)
        log(f"Dirección: {address}")

        # Extraer puntuación
        log("Extrayendo puntuación...")
        score_selectors = ['[data-testid="review-score-component"]', '.bui-review-score__badge']
        score = extract_fast(score_selectors)
        log(f"Puntuación: {score}")

        # Extraer precio
        log("Extrayendo precio...")
        price_selectors = [
            '[data-testid="price-and-discounted-price"]',
            '.bui-price-display__value',
            '.prco-inline-block-maker-helper',
            '.bui-price-display__original',
            '.sr-hotel__price-number'
        ]
        prices = []
        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    text = el.text.strip()
                    if text and any(char.isdigit() for char in text):
                        prices.append(text)
            except Exception:
                pass
        prices = list(set(prices))
        log(f"Precio: {prices}")

        # Extraer servicios/amenidades
        log("Extrayendo servicios/amenidades...")
        amenities_selectors = [
            '.hp-facilities__list .bui-list__item',
            '.hp-facilities__text',
            '[data-testid="facility-group-list"]',
            '.facility-highlights__list .bui-list__item',
            '.facility-highlights .bui-spacer--largest .bui-list__item'
        ]

        amenities = []
        for selector in amenities_selectors:
            amenities.extend(extract_fast(selector, multiple=True))

        amenities_set = set()
        unique_amenities = []
        for amenity in amenities:
            if amenity and amenity not in amenities_set:
                amenities_set.add(amenity)
                unique_amenities.append(amenity)

        amenities = unique_amenities[:20]
        log(f"Servicios/amenidades encontradas: {len(amenities)}")

        # Buscar imágenes
        log("Iniciando descarga de imágenes...")
        image_selectors = [
            'img[data-testid="photo-gallery-image"]',
            '.hp-gallery img',
            '.bh-photo-grid img',
            'img[alt*="hotel"]',
            'img[alt*="Hotel"]',
            '.hp-photogallery img',
            '.photos-container img'
        ]

        all_images = []
        img_index = 0

        for selector in image_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                log(f"Encontrados {len(elements)} elementos con selector: {selector}")
                
                for element in elements:
                    try:
                        img_url = element.get_attribute('src')
                        if not img_url or 'data:' in img_url:
                            img_url = element.get_attribute('data-src')
                        if not img_url or 'data:' in img_url:
                            img_url = element.get_attribute('data-lazy-src')
                            
                        if img_url and is_valid_image_url(img_url):
                            all_images.append({
                                'url': img_url,
                                'index': img_index,
                                'element': element
                            })
                            img_index += 1
                            
                    except Exception as e:
                        log(f"Error procesando elemento de imagen: {e}")
                        continue
                        
            except Exception as e:
                log(f"Error con selector {selector}: {e}")
                continue

        # Eliminar duplicados por URL
        seen_urls = set()
        valid_images = []

        for img in all_images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                valid_images.append(img)

        log(f"Total de imágenes únicas encontradas: {len(valid_images)}")

        # Seleccionar imágenes de forma balanceada
        if len(valid_images) > 15:
            selected_images = select_balanced_images(valid_images, 15)
        else:
            selected_images = valid_images

        log(f"Descargando {len(selected_images)} imágenes...")

        # Descargar las imágenes seleccionadas
        downloaded_images = []
        for i, img_data in enumerate(selected_images):
            category = img_data.get('category', 'general')
            local_path = download_image(img_data['url'], hotel_name or f"hotel_{i}", i, category)
            if local_path:
                downloaded_images.append(local_path)
                log(f"Imagen {i} descargada: {category}")

        log(f"Total de imágenes descargadas exitosamente: {len(downloaded_images)}")

        # Guardar datos en SQLite
        log("Guardando datos en base de datos...")
        db = sqlite3.connect('hoteles.db')
        c = db.cursor()

        # Crear tablas si no existen
        c.execute('''CREATE TABLE IF NOT EXISTS hotel
                     (id INTEGER PRIMARY KEY, 
                      nombre TEXT, 
                      direccion TEXT, 
                      puntuacion TEXT, 
                      precio TEXT,
                      amenidades TEXT,
                      fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        c.execute('''CREATE TABLE IF NOT EXISTS imagen
                     (id INTEGER PRIMARY KEY,
                      hotel_id INTEGER,
                      url TEXT,
                      local_path TEXT,
                      FOREIGN KEY (hotel_id) REFERENCES hotel (id))''')

        # Insertar datos del hotel
        amenidades_str = '; '.join(amenities) if amenities else ''
        precio_str = '; '.join(prices) if prices else ''

        c.execute('''INSERT INTO hotel (nombre, direccion, puntuacion, precio, amenidades) 
                     VALUES (?, ?, ?, ?, ?)''', 
                  (hotel_name, address, score, precio_str, amenidades_str))

        hotel_id = c.lastrowid

        # Insertar rutas de imágenes
        for local_path in downloaded_images:
            if local_path and os.path.exists(local_path):
                c.execute('INSERT INTO imagen (hotel_id, url, local_path) VALUES (?, ?, ?)', 
                          (hotel_id, '', local_path))

        db.commit()
        db.close()

        # Calcular tiempo total
        end_time = time.time()
        total_time = end_time - start_time
        log(f'Scraping completado en {total_time:.2f} segundos')
        log(f'Datos guardados en la base de datos SQLite.')
        
        return True
    
    except Exception as e:
        log(f"Error en scraping de {url}: {str(e)}")
        raise
    
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                log(f"Error al cerrar el navegador: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        url_mexico = adaptar_url_mexico(url)
        log(f"Iniciando scraping detallado para: {url_mexico}")
        try:
            scrape_hotel_full(url_mexico)
            log(f"Scraping completado para: {url_mexico}")
        except Exception as e:
            log(f"Error en scraping de {url_mexico}: {e}")
            sys.exit(1)
    else:
        print("Uso: python scrape_booking.py <url_del_hotel>")
        print("O ejecuta el lanzador run_parallel.py para scraping masivo.")
