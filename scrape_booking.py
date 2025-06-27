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
        
        def select_balanced_images(valid_images, target_count=15):
            """Selecciona imágenes de forma balanceada por categorías usando análisis visual"""
            log("Clasificando imágenes usando análisis visual...")
            
            for i, img in enumerate(valid_images):
                image_data = None
                if visual_classifier:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        response = requests.get(img['url'], headers=headers, timeout=10)
                        if response.status_code == 200:
                            image_data = response.content
                    except:
                        pass
                
                img['category'] = classify_image_type(img['url'], img_index=i, image_data=image_data)
                log(f"Imagen {i+1}: {img['category']} - {img['url'][:80]}...")
            
            categories = {}
            for img in valid_images:
                cat = img['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(img)
            
            log("Distribución de categorías encontradas:")
            for cat, imgs in categories.items():
                log(f"  {cat}: {len(imgs)} imágenes")
            
            desired_distribution = {
                'habitacion': 5,
                'exterior': 3,
                'piscina': 2,
                'baño': 2,
                'restaurante': 2,
                'general': 1
            }
            
            selected_images = []
            for category, desired_count in desired_distribution.items():
                if category in categories:
                    cat_images = sorted(categories[category], key=lambda x: (x['priority'], x['area']), reverse=True)
                    selected_from_cat = cat_images[:desired_count]
                    selected_images.extend(selected_from_cat)
                    log(f"Categoría '{category}': {len(selected_from_cat)}/{desired_count} imágenes seleccionadas")
            
            if len(selected_images) < target_count:
                remaining_images = [img for img in valid_images if img not in selected_images]
                remaining_images.sort(key=lambda x: (x['priority'], x['area']), reverse=True)
                needed = target_count - len(selected_images)
                selected_images.extend(remaining_images[:needed])
                log(f"Completando con {needed} imágenes adicionales")
            
            final_selection = selected_images[:target_count]
            final_categories = {}
            for img in final_selection:
                cat = img['category']
                final_categories[cat] = final_categories.get(cat, 0) + 1
            
            log(f"Distribución final seleccionada: {final_categories}")
            return final_selection
        
        def edit_image_with_white_pixels(filepath):
            """Edita la imagen agregando píxeles casi imperceptibles que se mezclen con la imagen"""
            try:
                with Image.open(filepath) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    draw = ImageDraw.Draw(img)
                    width, height = img.size
                    num_pixels = random.randint(2, 4)
                    
                    for _ in range(num_pixels):
                        x = random.randint(0, width - 3)
                        y = random.randint(0, height - 3)
                        original_pixel = img.getpixel((x, y))
                        r, g, b = original_pixel
                        new_r = min(255, r + random.randint(1, 3))
                        new_g = min(255, g + random.randint(1, 3))
                        new_b = min(255, b + random.randint(1, 3))
                        subtle_color = (new_r, new_g, new_b)
                        
                        if random.random() < 0.6:
                            draw.point((x, y), fill=subtle_color)
                        else:
                            for px in range(2):
                                for py in range(2):
                                    if x + px < width and y + py < height:
                                        pixel_color = (
                                            min(255, new_r + random.randint(-1, 1)),
                                            min(255, new_g + random.randint(-1, 1)),
                                            min(255, new_b + random.randint(-1, 1))
                                        )
                                        draw.point((x + px, y + py), fill=pixel_color)
                    
                    img.save(filepath, 'JPEG', quality=99)
            except Exception as e:
                log(f"Error editando imagen: {str(e)}")
        
        def download_and_edit_images(urls, hotel_id, hotel_name):
            """Descarga imágenes, evita duplicados, filtra por tamaño y las edita con píxeles blancos"""
            # Crear directorio base de imágenes
            if not os.path.exists('imagenes'):
                os.makedirs('imagenes')
            
            # Crear subdirectorio específico para el hotel
            # Limpiar el nombre del hotel para usarlo como nombre de carpeta
            clean_hotel_name = hotel_name or 'hotel_sin_nombre'
            clean_hotel_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', clean_hotel_name)
            clean_hotel_name = re.sub(r'[^\w\s-]', '_', clean_hotel_name)
            clean_hotel_name = re.sub(r'\s+', '_', clean_hotel_name)
            clean_hotel_name = clean_hotel_name.strip('_')[:50]  # Limitar longitud y quitar _ del inicio/final
            hotel_folder = os.path.join('imagenes', f'hotel_{hotel_id}_{clean_hotel_name}')
            if not os.path.exists(hotel_folder):
                os.makedirs(hotel_folder)
                log(f"Creada carpeta para hotel: {hotel_folder}")
            
            # Variable para retornar las rutas de las imágenes descargadas
            downloaded_images = []
            
            downloaded_hashes = set()
            valid_images = []
            
            log("Filtrando imágenes por tamaño (criterios relajados)...")
            
            for i, url_img in enumerate(urls[:40]):
                try:
                    log(f"Verificando imagen {i+1}/{min(len(urls), 40)}...")
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    head_response = requests.head(url_img, headers=headers, timeout=5)
                    if head_response.status_code != 200:
                        continue
                    
                    response = requests.get(url_img, headers=headers, timeout=10)
                    if response.status_code == 200:
                        image_hash = hashlib.md5(response.content).hexdigest()
                        if image_hash in downloaded_hashes:
                            log(f"Imagen duplicada, saltando...")
                            continue
                        
                        try:
                            with Image.open(requests.get(url_img, headers=headers, stream=True).raw) as img:
                                width, height = img.size
                                area = width * height
                                is_large_square = width >= 600 and height >= 600
                                is_good_rectangle = (width >= 800 and height >= 400) or (width >= 400 and height >= 800)
                                has_good_area = area >= 240000
                                
                                if is_large_square or is_good_rectangle or has_good_area:
                                    priority = 0
                                    if width >= 900 and height >= 900:
                                        priority = 3
                                    elif width >= 700 and height >= 700:
                                        priority = 2
                                    elif area >= 400000:
                                        priority = 1
                                    else:
                                        priority = 0
                                    
                                    valid_images.append({
                                        'url': url_img,
                                        'hash': image_hash,
                                        'size': (width, height),
                                        'area': area,
                                        'priority': priority
                                    })
                                    downloaded_hashes.add(image_hash)
                                    log(f"Imagen válida: {width}x{height} (prioridad: {priority})")
                                else:
                                    log(f"Imagen muy pequeña ({width}x{height}), descartada")
                        except Exception as e:
                            log(f"Error verificando dimensiones: {str(e)}")
                except Exception as e:
                    log(f"Error verificando imagen {i+1}: {str(e)}")
            
            selected_images = select_balanced_images(valid_images, 15)
            log(f"Seleccionadas {len(selected_images)} imágenes balanceadas para descargar (de {len(valid_images)} válidas)")
            
            for i, img_info in enumerate(selected_images):
                try:
                    url_img = img_info['url']
                    image_hash = img_info['hash']
                    width, height = img_info['size']
                    priority = img_info['priority']
                    category = img_info['category']
                    
                    log(f"Descargando imagen {i+1}/{len(selected_images)} ({width}x{height}, {category}, prioridad {priority})...")
                    
                    response = requests.get(url_img, headers=headers, timeout=10)
                    if response.status_code == 200:
                        filename = f'hotel_{hotel_id}_img_{i+1}_{category}_{image_hash[:8]}_{width}x{height}_p{priority}.jpg'
                        filepath = os.path.join(hotel_folder, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        edit_image_with_white_pixels(filepath)
                        downloaded_images.append((filepath, url_img))  # Guardar tupla con filepath y URL original
                        log(f"Imagen guardada y editada: {os.path.join(os.path.basename(hotel_folder), filename)}")
                except Exception as e:
                    log(f"Error descargando imagen {i+1}: {str(e)}")
            
            return downloaded_images
        
        def safe_str(val):
            if val is None:
                return ''
            if isinstance(val, list):
                return '\n'.join([str(v) for v in val])
            return str(val)
        
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
        
        # Mejorar búsqueda de dirección
        if not address:
            try:
                meta_address = driver.execute_script('''
                    let metas = document.getElementsByTagName('meta');
                    for (let m of metas) {
                        if (m.getAttribute('property') && m.getAttribute('property').toLowerCase().includes('street-address')) {
                            return m.getAttribute('content');
                        }
                        if (m.getAttribute('name') && m.getAttribute('name').toLowerCase().includes('address')) {
                            return m.getAttribute('content');
                        }
                    }
                    return null;
                ''')
                if meta_address:
                    address = meta_address
            except Exception as e:
                log(f"Error buscando dirección en meta tags: {e}")
        
        if not address:
            try:
                html = driver.page_source
                match = re.search(r'(Calle|Avenida|Av\.|Plaza|Paseo|Camino|Carretera)[^<,\n]+\d+[^<,\n]*,[^<\n]+', html)
                if match:
                    address = match.group(0)
            except Exception as e:
                log(f"Error buscando dirección con regex: {e}")
        
        if not address:
            try:
                html = driver.page_source
                match = re.search(r'"addressLine2"\s*:\s*"([^"]+)".*?"city"\s*:\s*"([^"]+)".*?"postalCode"\s*:\s*"([^"]+)".*?"countryCode"\s*:\s*"([^"]+)"', html, re.DOTALL)
                if match:
                    calle = match.group(1)
                    ciudad = match.group(2)
                    postal = match.group(3)
                    pais = match.group(4).upper()
                    address = f"{calle}, {postal} {ciudad}, {pais}"
            except Exception as e:
                log(f"Error buscando dirección estructurada en JSON: {e}")
        
        # Limpiar dirección
        if address:
            address = address.replace('\n', ' ').replace('\r', ' ')
            address = re.sub(r'\s+', ' ', address).strip()
            address = re.sub(r'Mostrar en el mapa.*$', '', address, flags=re.IGNORECASE).strip()
        
        log(f"Dirección: {address}")
        
        # Extraer puntuación
        log("Extrayendo puntuación...")
        score_selectors = ['[data-testid="review-score-component"]', '.bui-review-score__badge']
        score = extract_fast(score_selectors)
        log(f"Puntuación: {score}")
        
        # Extraer precios
        log("Extrayendo precios...")
        price_selectors = [
            '[data-testid="price-and-discounted-price"]',
            '.pricerow_price',
            '.bui-price-display__value',
            '.hprt-price-block'
        ]
        prices = []
        for selector in price_selectors:
            found_prices = fast_get_text(selector, multiple=True)
            if found_prices:
                prices.extend(found_prices)
                break
        prices = list(set(prices))
        log(f"Precios: {prices}")
        
        # Extraer amenities
        log("Extrayendo amenities...")
        amenities_selectors = [
            '[data-testid="facilities-list"] li',
            '.hotel-facilities-group li',
            '.important_facility',
            '.facilitiesChecklistSection li',
            '.hp-description__list li',
            '.facility-badge',
            '.bui-list__item',
            '.hotel-facilities li',
            '.facilities-block li'
        ]
        amenities = []
        for selector in amenities_selectors:
            found_amenities = fast_get_text(selector, multiple=True)
            if found_amenities:
                amenities.extend(found_amenities)
        
        if not amenities:
            log("Intentando método alternativo para amenities...")
            try:
                service_keywords = ['WiFi', 'Wi-Fi', 'Internet', 'Aire acondicionado', 'Parking', 'Aparcamiento', 
                                  'Piscina', 'Gimnasio', 'Spa', 'Desayuno', 'Restaurante', 'Bar', 'Recepción']
                for keyword in service_keywords:
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                    for elem in elements:
                        parent_text = elem.text.strip()
                        if parent_text and len(parent_text) < 100:
                            amenities.append(parent_text)
            except:
                pass
        
        amenities = list(set(amenities))
        log(f"Amenities: {len(amenities)} encontrados - {amenities[:5]}{'...' if len(amenities) > 5 else ''}")
        
        # Extraer descripción
        log("Extrayendo descripción...")
        description_selectors = ['[data-testid="property-description"]', '.hotel_description_wrapper_exp']
        description = extract_fast(description_selectors)
        log(f"Descripción: {'Encontrada' if description else 'No encontrada'}")
        
        # Extraer tipos de habitaciones
        log("Extrayendo tipos de habitaciones...")
        room_selectors = ['[data-testid="room-name"]', '.hprt-table-cell-roomtype']
        room_types = []
        for selector in room_selectors:
            found_rooms = fast_get_text(selector, multiple=True)
            if found_rooms:
                room_types = found_rooms
                break
        log(f"Habitaciones: {len(room_types)} tipos encontrados")
        
        # Extraer imágenes en alta calidad
        log("Extrayendo imágenes en alta calidad...")
        driver.execute_script("document.querySelectorAll('img').forEach(img => img.src = img.dataset.src || img.src);")
        time.sleep(2)
        
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'img[src*="jpg"], img[src*="jpeg"], img[src*="png"]')
        image_urls = []
        
        for img in image_elements:
            src = img.get_attribute('src')
            if src and any(ext in src for ext in ['jpg', 'jpeg', 'png']):
                high_quality_url = src
                
                # Convertir URLs a la máxima calidad posible
                if 'max300' in src:
                    high_quality_url = src.replace('max300', 'max1920')
                elif 'max400' in src:
                    high_quality_url = src.replace('max400', 'max1920')
                elif 'max500' in src:
                    high_quality_url = src.replace('max500', 'max1920')
                elif 'max800' in src:
                    high_quality_url = src.replace('max800', 'max1920')
                elif 'max1024' in src:
                    high_quality_url = src.replace('max1024', 'max1920')
                elif 'square60' in src:
                    high_quality_url = src.replace('square60', 'max1920')
                elif 'square200' in src:
                    high_quality_url = src.replace('square200', 'max1920')
                elif 'square300' in src:
                    high_quality_url = src.replace('square300', 'max1920')
                
                if 'booking.com' in src and not 'orig' in src:
                    orig_url = src.replace('.jpg', '_orig.jpg').replace('.jpeg', '_orig.jpeg')
                    image_urls.append(orig_url)
                
                image_urls.append(high_quality_url)
        
        image_urls = list(set(image_urls))
        priority_urls = []
        regular_urls = []
        
        for url_img in image_urls:
            if any(pattern in url_img for pattern in ['max1920', 'orig', 'max1600', 'max1200']):
                priority_urls.append(url_img)
            else:
                regular_urls.append(url_img)
        
        final_urls = priority_urls + regular_urls
        log(f"URLs de imágenes encontradas: {len(final_urls)} (priorizando alta calidad)")
        
        # Primero guardamos la información básica del hotel para obtener el ID
        log("Guardando información básica del hotel en la base de datos...")
        db = sqlite3.connect('hoteles.db')
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS hotel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            direccion TEXT,
            puntuacion TEXT,
            descripcion TEXT,
            precios TEXT,
            amenities TEXT,
            habitaciones TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS imagen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER,
            url TEXT,
            local_path TEXT,
            FOREIGN KEY(hotel_id) REFERENCES hotel(id)
        )''')
        
        data = tuple(safe_str(x) for x in [
            hotel_name,
            address,
            score,
            description,
            prices,
            amenities,
            room_types
        ])
        
        c.execute('''INSERT INTO hotel (nombre, direccion, puntuacion, descripcion, precios, amenities, habitaciones)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
        hotel_id = c.lastrowid
        log(f"Hotel guardado con ID: {hotel_id}")
        
        # Ahora descargamos las imágenes usando el ID real del hotel
        downloaded_images = download_and_edit_images(final_urls, hotel_id, hotel_name)
        log(f"Total de imágenes descargadas y editadas: {len(downloaded_images)}")
        
        # Guardar información de imágenes en la base de datos
        for filepath, original_url in downloaded_images:
            if filepath and os.path.exists(filepath):
                c.execute('INSERT INTO imagen (hotel_id, url, local_path) VALUES (?, ?, ?)', 
                          (hotel_id, original_url, filepath))
        
        db.commit()
        db.close()
        log(f"Información de {len(downloaded_images)} imágenes guardada en la base de datos")
        
        # Extraer servicios/amenidades adicionales
        log("Extrayendo amenities (servicios) desde la sección principal...")
        servicios = []
        try:
            servicios_section = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="property-section--content"]')
            grupos = servicios_section.find_elements(By.CSS_SELECTOR, 'ul, div[data-testid="facility-group-container"]')
            for grupo in grupos:
                items = grupo.find_elements(By.CSS_SELECTOR, 'li')
                for item in items:
                    texto = item.text.strip()
                    if texto and texto not in servicios:
                        servicios.append(texto)
        except Exception as e:
            log(f"No se pudo extraer servicios desde la sección principal: {e}")
        
        if not servicios:
            try:
                items = driver.find_elements(By.CSS_SELECTOR, 'li')
                for item in items:
                    spans = item.find_elements(By.CSS_SELECTOR, 'span[data-testid*="facility-icon"], span[data-testid*="amenity-icon"]')
                    if spans:
                        texto = item.text.strip()
                        if texto and texto not in servicios:
                            servicios.append(texto)
            except Exception as e:
                log(f"Método alternativo de servicios falló: {e}")
        
        log(f"Servicios/Amenidades extraídos: {len(servicios)} encontrados")
        for s in servicios:
            log(f"  - {s}")
        
        # Combinar amenities
        if servicios:
            all_amenities = set([a.strip() for a in amenities if a and a.strip()]) | set([s.strip() for s in servicios if s and s.strip()])
            amenities = list(all_amenities)
            log(f"Amenities combinados (sin duplicados): {len(amenities)}")
        
        # Calcular tiempo total
        end_time = time.time()
        total_time = end_time - start_time
        log(f'Scraping completado en {total_time:.2f} segundos')
        log(f'Datos guardados en la base de datos SQLite.')
        
    except Exception as e:
        log(f"Error en scraping: {str(e)}")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        url_mexico = adaptar_url_mexico(url)
        log(f"Iniciando scraping detallado para: {url_mexico}")
        scrape_hotel_full(url_mexico)
    else:
        print("Uso: python scrape_booking.py <url_del_hotel>")
        print("O ejecuta el lanzador run_parallel.py para scraping masivo.")
