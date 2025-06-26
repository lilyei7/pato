import time
import json
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException

def log(msg):
    print(f"[LOG] {msg}")

# Configura el path al geckodriver y Firefox
service = Service("./geckodriver.exe")
options = Options()
options.headless = False  # Para ver el resultado visualmente
options.binary_location = r"C:\Program Files\Firefox Developer Edition\firefox.exe"

dashboard_url = "https://www.airbnb.com/hosting/listings"

log("Abriendo navegador para comprobar sesión y crear anuncio...")
driver = webdriver.Firefox(service=service, options=options)
driver.get("https://www.airbnb.com/")

# Cargar cookies guardadas
try:
    with open("cookies_airbnb.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        cookie.pop('sameSite', None)
        driver.add_cookie(cookie)
    log(f"Cookies cargadas ({len(cookies)})")
except Exception as e:
    log(f"ERROR al cargar cookies: {e}")
    driver.quit()
    exit(1)

# Ir al dashboard de anfitrión
log("Refrescando página y navegando al dashboard de anfitrión...")
driver.get(dashboard_url)
wait = WebDriverWait(driver, 30)

# Esperar a que el menú de anfitrión esté presente (más tolerante y con log de HTML para depuración)
try:
    log("Esperando a que el menú de anfitrión esté visible...")
    wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜ','abcdefghijklmnopqrstuvwxyzáéíóúü'), 'alojamientos') or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜ','abcdefghijklmnopqrstuvwxyzáéíóúü'), 'hosting') or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜ','abcdefghijklmnopqrstuvwxyzáéíóúü'), 'anfitrión')]"
    )))
    log("¡Menú de anfitrión detectado! Esperando 3 segundos extra para asegurar carga completa...")
    time.sleep(3)
except Exception as e:
    log(f"No se detectó el menú de anfitrión: {e}")
    log(f"HTML actual: {driver.page_source[:2000]}")  # Muestra los primeros 2000 caracteres del HTML para depurar
    driver.save_screenshot('error_menu_anfitrion.png')
    driver.quit()
    exit(1)

# Ir directo a la URL de creación de anuncio (overview)
try:
    crear_url = "https://www.airbnb.mx/become-a-host/overview"
    log(f"Navegando a la URL de creación de anuncio: {crear_url}")
    driver.get(crear_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    log("Página de creación de anuncio cargada. Automatizando flujo inicial...")
    time.sleep(2)

    # 1. Click en "Empieza" (con scroll y fallback JS)
    try:
        empieza_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Empieza']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", empieza_btn)
        time.sleep(0.5)
        try:
            empieza_btn.click()
        except Exception as e:
            log(f"Click normal en 'Empieza' falló, intentando con JavaScript: {e}")
            driver.execute_script("arguments[0].click();", empieza_btn)
        log("Click en 'Empieza' OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Empieza': {e}")
        driver.save_screenshot('error_empieza.png')
        raise

    # 2. Click en "Empieza por tu cuenta"
    try:
        empieza_solo_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Empieza por tu cuenta']")))
        empieza_solo_btn.click()
        log("Click en 'Empieza por tu cuenta' OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Empieza por tu cuenta': {e}")
        driver.save_screenshot('error_empieza_solo.png')
        raise

    # 3. Click en "Siguiente"
    try:
        siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Siguiente']")))
        siguiente_btn.click()
        log("Click en 'Siguiente' OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Siguiente': {e}")
        driver.save_screenshot('error_siguiente.png')
        raise

    # 4. Click en "Departamento" (más genérico, usando solo el texto 'Departamento')
    try:
        depto_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Departamento']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", depto_btn)
        time.sleep(0.5)
        try:
            depto_btn.click()
        except Exception as e:
            log(f"Click normal en 'Departamento' falló, intentando con JavaScript: {e}")
            driver.execute_script("arguments[0].click();", depto_btn)
        log("Click en 'Departamento' OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Departamento': {e}")
        driver.save_screenshot('error_departamento.png')
        raise

    # 5. Click en "Siguiente" después de seleccionar "Departamento"
    try:
        siguiente2_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente2_btn)
        time.sleep(0.5)
        try:
            siguiente2_btn.click()
        except Exception as e:
            log(f"Click normal en 'Siguiente' (después de Departamento) falló, intentando con JavaScript: {e}")
            driver.execute_script("arguments[0].click();", siguiente2_btn)
        log("Click en 'Siguiente' (después de Departamento) OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Siguiente' (después de Departamento): {e}")
        driver.save_screenshot('error_siguiente2.png')
        raise

    # 6. Click en "Una habitación"
    try:
        una_hab_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//h2[text()='Una habitación']/ancestor::button")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", una_hab_btn)
        time.sleep(0.5)
        try:
            una_hab_btn.click()
        except Exception as e:
            log(f"Click normal en 'Una habitación' falló, intentando con JavaScript: {e}")
            driver.execute_script("arguments[0].click();", una_hab_btn)
        log("Click en 'Una habitación' OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Una habitación': {e}")
        driver.save_screenshot('error_unahabitacion.png')
        raise

    # 7. Click en "Siguiente" tras seleccionar "Una habitación"
    try:
        siguiente3_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente3_btn)
        time.sleep(0.5)
        try:
            siguiente3_btn.click()
        except Exception as e:
            log(f"Click normal en 'Siguiente' (después de Una habitación) falló, intentando con JavaScript: {e}")
            driver.execute_script("arguments[0].click();", siguiente3_btn)
        log("Click en 'Siguiente' (después de Una habitación) OK")
        time.sleep(2)
    except Exception as e:
        log(f"No se pudo hacer click en 'Siguiente' (después de Una habitación): {e}")
        driver.save_screenshot('error_siguiente3.png')
        raise

    # 8. Click en el input de dirección ("Ingresa tu dirección") y escribe la dirección completa bien formateada desde la base de datos
    try:
        import sqlite3, re
        db = sqlite3.connect('hoteles.db')
        c = db.cursor()
        c.execute('SELECT direccion FROM hotel ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        direccion_db = row[0] if row else ''
        db.close()
        log(f"Dirección obtenida de la base de datos: {direccion_db}")

        # Buscar todos los datos con regex: calle, cp, ciudad, país
        # Ejemplo esperado: 'Calle Campezo 4, 28022 Madrid, ES'
        calle, cp, ciudad, pais = '', '', '', ''
        # Buscar calle
        calle_match = re.search(r'([A-ZÁÉÍÓÚa-záéíóúñÑ ]+\d+[A-Za-z]?)', direccion_db)
        if calle_match:
            calle = calle_match.group(1).strip()
        # Buscar CP
        cp_match = re.search(r'(\d{4,6})', direccion_db)
        if cp_match:
            cp = cp_match.group(1).strip()
        # Buscar ciudad
        ciudad_match = re.search(r'"city"\s*:\s*"([^"]+)"', direccion_db)
        if ciudad_match:
            ciudad = ciudad_match.group(1).strip()
        else:
            # Fallback: buscar ciudad después del CP
            ciudad_fallback = re.search(r'\d{4,6}\s+([A-ZÁÉÍÓÚa-záéíóúñÑ ]+)', direccion_db)
            if ciudad_fallback:
                ciudad = ciudad_fallback.group(1).strip()
        # Buscar país
        pais_match = re.search(r'"countryCode"\s*:\s*"([A-Za-z]{2,3})"', direccion_db)
        if pais_match:
            pais = pais_match.group(1).upper().strip()
        else:
            # Fallback: buscar país al final
            pais_fallback = re.findall(r',\s*([A-Za-z]{2,3})$', direccion_db)
            if pais_fallback:
                pais = pais_fallback[-1].upper().strip()
        # Construir dirección final
        direccion_final = calle
        if cp:
            direccion_final += f', {cp}'
        if ciudad:
            direccion_final += f' {ciudad}'
        if pais:
            direccion_final += f', {pais}'
        direccion_final = direccion_final.strip(', ')
        log(f"Dirección formateada para Airbnb: {direccion_final}")

        direccion_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Ingresa tu dirección']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", direccion_input)
        direccion_input.click()
        time.sleep(0.5)
        direccion_input.clear()
        direccion_input.send_keys(direccion_final)
        log("Dirección completa escrita en el input.")
        time.sleep(1)

        # Confirmar la ubicación haciendo click en la primera sugerencia
        try:
            sugerencia = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div._1av40jj")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sugerencia)
            time.sleep(0.5)
            sugerencia.click()
            log("Click en la primera sugerencia de dirección OK")
            time.sleep(2)
        except Exception as e:
            log(f"No se pudo hacer click en la sugerencia de dirección: {e}")
            driver.save_screenshot('error_sugerencia_direccion.png')
            raise
    except Exception as e:
        log(f"Error al ingresar la dirección o automatizar los pasos de dirección: {e}")
        driver.save_screenshot('error_direccion.png')
        raise

    # --- Automatización de pasos: Siguiente -> Siguiente -> Sí (cerradura) -> Siguiente ---
    try:
        # 1. Click en "Siguiente" (aria-label="Siguiente paso")
        siguiente_btn1 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn1)
        time.sleep(0.5)
        siguiente_btn1.click()
        log("Click en 'Siguiente' (después de dirección) OK")
        time.sleep(2)

        # 2. Click en "Siguiente" nuevamente
        siguiente_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn2)
        time.sleep(0.5)
        siguiente_btn2.click()
        log("Click en 'Siguiente' (después de paso intermedio) OK")
        time.sleep(2)

        # 3. Seleccionar el radio "Sí" para la cerradura
        radio_si = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='bedroom_lock_feature_radio_group'][value='locks_true']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_si)
        time.sleep(0.5)
        radio_si.click()
        log("Radio 'Sí' (cerradura) seleccionado OK")
        time.sleep(1)

        # 4. Click en "Siguiente" final
        siguiente_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn3)
        time.sleep(0.5)
        siguiente_btn3.click()
        log("Click en 'Siguiente' (después de cerradura) OK")
        time.sleep(2)
    except Exception as e:
        log(f"Error en la secuencia Siguiente->Siguiente->Sí->Siguiente: {e}")
        driver.save_screenshot('error_siguiente_habitaciones.png')
        raise
    # --- Fin de la automatización de pasos ---
            
    # --- Automatización: 2 clicks en ENSUITE, 4 clicks en DEDICATED, luego Siguiente ---
    try:
        # 1. Dos clicks en el botón "Agregar" ENSUITE
        for i in range(2):
            btn_ensuite = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='stepper-item--0-ENSUITE-stepper-increase-button']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_ensuite)
            time.sleep(0.3)
            btn_ensuite.click()
            log(f"Click {i+1}/2 en 'Agregar ENSUITE' OK")
            time.sleep(0.7)

        # 2. Cuatro clicks en el botón "Agregar" DEDICATED
        for i in range(4):
            btn_dedicated = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='stepper-item--1-DEDICATED-stepper-increase-button']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_dedicated)
            time.sleep(0.3)
            btn_dedicated.click()
            log(f"Click {i+1}/4 en 'Agregar DEDICATED' OK")
            time.sleep(0.7)

        # 3. Click en Siguiente (aria-label="Siguiente paso")
        siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
        time.sleep(0.5)
        siguiente_btn.click()
        log("Click en 'Siguiente' después de steppers OK")
        time.sleep(2)
    except Exception as e:
        log(f"Error en la automatización de steppers y siguiente: {e}")
        driver.save_screenshot('error_stepper_Habitaciones.png')
        raise
    # --- Fin automatización steppers ---

    # --- Click en Siguiente -> Siguiente antes de amenidades ---
    try:
        for i in range(2):
            siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
            time.sleep(0.5)
            siguiente_btn.click()
            log(f"Click {i+1}/2 en 'Siguiente' antes de amenidades OK")
            time.sleep(2)
    except Exception as e:
        log(f"Error haciendo click en Siguiente antes de amenidades: {e}")
        driver.save_screenshot('error_siguiente_amenidades.png')
        raise

    # --- Selección de amenidades usando Gemini (IA gratuita de Google) ---
    try:
        import sqlite3
        import requests
        import json as pyjson
        db = sqlite3.connect('hoteles.db')
        c = db.cursor()
        c.execute('SELECT amenities FROM hotel ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        db.close()
        if not row or not row[0]:
            log('No se encontraron amenidades en la base de datos.')
            raise Exception('No hay amenidades para seleccionar.')
        # Limpiar y dividir amenidades (por coma, salto de línea y punto y coma)
        raw_amenities = row[0]
        amenities_db = set()
        for part in raw_amenities.split(','):
            for subpart in part.split('\n'):
                for item in subpart.split(';'):
                    clean = item.strip().lower()
                    if clean and len(clean) < 50:
                        amenities_db.add(clean)
        amenities_db = list(amenities_db)
        log(f"Amenidades limpias para IA: {amenities_db}")

        # --- Mejor comparación: normaliza y traduce las opciones de la UI para mejor matching ---
        def normalize(text):
            return text.strip().lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ü','u').replace('ñ','n')        # Diccionario de sinónimos y equivalencias comunes para amenidades
        equivalencias = {
            'wifi': ['wifi', 'internet', 'internet wifi', 'wi-fi', 'conexion a internet', 'conexión a internet', 'internet de alta velocidad'],
            'aire acondicionado': ['aire acondicionado', 'ac', 'a/c', 'clima', 'climatizacion', 'climatización'],
            'gimnasio': ['gimnasio', 'equipo para hacer ejercicio', 'zona fitness', 'fitness', 'centro de fitness', 'equipos de gimnasio'],
            'alberca': ['alberca', 'piscina', 'pool', 'swimming pool', 'pileta', 'piscina exterior', 'piscina interior', 'piscina cubierta'],
            'jacuzzi': ['jacuzzi', 'tina de hidromasaje', 'tina de hidromasaje/jacuzzi', 'hot tub', 'hidromasaje'],
            'asador': ['asador', 'parrilla', 'barbacoa', 'bbq', 'parrilla para barbacoa', 'area de barbacoa'],
            'patio': ['patio', 'terraza', 'balcon', 'balcón'],
            'comedor al aire libre': ['comedor al aire libre', 'area para comer al aire libre', 'área para comer al aire libre', 'mesa exterior', 'comedor exterior'],
            'lavadora': ['lavadora', 'lavadora de ropa', 'maquina de lavar'],
            'cocina': ['cocina', 'kitchenette', 'cocineta', 'cocina equipada', 'cocina completa'],
            'tv': ['tv', 'television', 'televisión', 'televisor', 'smart tv', 'tv por cable'],
            'estacionamiento gratuito en las instalaciones': ['estacionamiento gratuito en las instalaciones', 'parking', 'estacionamiento', 'parking gratuito', 'estacionamiento gratis', 'aparcamiento'],
            'estacionamiento de pago en las instalaciones': ['estacionamiento de pago en las instalaciones', 'parking de pago', 'estacionamiento pago'],
            'mesa de billar': ['mesa de billar', 'billar', 'billiard', 'pool table'],
            'chimenea interior': ['chimenea interior', 'chimenea', 'fogata interior'],
            'piano': ['piano', 'teclado musical'],
            'acceso al lago': ['acceso al lago', 'vista al lago', 'frente al lago'],
            'acceso a la playa': ['acceso a la playa', 'frente a la playa', 'vista al mar', 'frente al mar'],
            'regadera exterior': ['regadera exterior', 'ducha exterior', 'ducha al aire libre'],
            'detector de humo': ['detector de humo', 'alarma de humo', 'detector de incendios'],
            'botiquin': ['botiquin', 'botiquín', 'kit de primeros auxilios', 'primeros auxilios'],
            'extintor de incendios': ['extintor de incendios', 'extintor', 'matafuegos'],
            'detector de monoxido de carbono': ['detector de monoxido de carbono', 'detector de monóxido de carbono', 'alarma de co'],
            'recepcion 24 horas': ['recepcion 24 horas', 'recepción 24 horas', 'recepción 24h', 'recepcion 24h', 'servicio de recepcion 24 horas'],
            'desayuno': ['desayuno', 'desayuno disponible', 'desayuno • almuerzo • cena', 'servicio de desayuno', 'desayuno incluido', 'desayuno continental'],
            'restaurante': ['restaurante', 'restaurantes', 'servicio de restaurante', 'restaurante en el lugar'],
            'area para trabajar': ['area para trabajar', 'área para trabajar', 'espacio de trabajo', 'escritorio', 'mesa de trabajo'],
            'lugar para hacer fogata': ['lugar para hacer fogata', 'fogata', 'fogata exterior', 'area de fogata', 'pit de fogata'],
            'spa': ['spa', 'servicios de spa', 'centro de spa', 'spa en el lugar'],
            'sauna': ['sauna', 'sauna seca', 'baño de vapor', 'sauna finlandesa'],
            'secadora': ['secadora', 'secadora de ropa'],
            'calefaccion': ['calefaccion', 'calefacción', 'heating', 'calefactor'],
            'vista': ['vista', 'vista panoramica', 'vista panorámica', 'vistas', 'vista a la ciudad'],
            'cafetera': ['cafetera', 'cafetera expreso', 'cafetera nespresso', 'maquina de cafe'],
            'microondas': ['microondas', 'horno microondas'],
            'nevera': ['nevera', 'refrigerador', 'frigorífico', 'frigorifico', 'heladera', 'refrigerador mini', 'mini refrigerador'],
            'lavavajillas': ['lavavajillas', 'lavaplatos', 'dishwasher'],
            'caja fuerte': ['caja fuerte', 'caja de seguridad'],
            'ascensor': ['ascensor', 'elevador'],
            'servicio de limpieza': ['servicio de limpieza', 'limpieza', 'limpieza diaria', 'servicio de limpieza diario'],
            'secador de pelo': ['secador de pelo', 'secador', 'hair dryer'],
            'plancha': ['plancha', 'plancha de ropa', 'tabla de planchar'],
            'cuna': ['cuna', 'cuna para bebés', 'cuna para bebes'],
            'zona de juegos': ['zona de juegos', 'area de juegos', 'juegos', 'sala de juegos'],
            'room service': ['room service', 'servicio a la habitacion', 'servicio a la habitación'],
            'servicio de conserjeria': ['servicio de conserjeria', 'servicio de conserjería', 'concierge', 'conserjeria', 'conserjería'],
            'caja de seguridad': ['caja de seguridad', 'caja fuerte'],
            'bano privado': ['bano privado', 'baño privado', 'baño en suite', 'bano en suite', 'baño dentro de la habitación'],
            'bano compartido': ['bano compartido', 'baño compartido'],
            'ropa de cama': ['ropa de cama', 'sabanas', 'sábanas', 'almohadas'],
            'toallas': ['toallas', 'toallas de baño'],
            'mascotas permitidas': ['mascotas permitidas', 'pet friendly', 'se admiten mascotas'],
            'servicio de transporte': ['servicio de transporte', 'traslado', 'shuttle', 'transporte al aeropuerto'],
            'entrada independiente': ['entrada independiente', 'entrada privada', 'acceso privado'],
            'servicio de lavanderia': ['servicio de lavanderia', 'servicio de lavandería', 'lavanderia', 'lavandería'],
            'alquiler de bicicletas': ['alquiler de bicicletas', 'bicicletas', 'renta de bicicletas', 'bicis disponibles'],
            'mini bar': ['mini bar', 'minibar', 'refrigerador con bebidas'],
            'area de estar': ['area de estar', 'área de estar', 'zona de estar', 'living', 'sala', 'sala de estar'],
            'habitacion doble': ['habitacion doble', 'habitación doble', 'cama doble', 'cama matrimonial'],
            'habitacion individual': ['habitacion individual', 'habitación individual', 'cama individual', 'cama sencilla'],
            'aparcamiento': ['aparcamiento', 'parking', 'estacionamiento', 'garage', 'garaje'],
        }# Primero, normaliza y expande las amenidades de la base de datos
        amenities_db_norm = set()
        for amenity in amenities_db:
            n = normalize(amenity)
            amenities_db_norm.add(n)
            # Agrega equivalencias si existen
            for key, vals in equivalencias.items():
                if n in vals:
                    amenities_db_norm.update(vals)
        log(f"Amenidades de la base de datos (normalizadas y expandidas): {list(amenities_db_norm)}")
        
        # Busca botones de amenidades por su rol de checkbox en lugar de solo labels
        amenity_buttons = driver.find_elements(By.XPATH, "//button[@role='checkbox']")
        log(f"Encontrados {len(amenity_buttons)} botones de amenidades por rol checkbox")
        
        # Si no hay botones, intenta buscar por otros selectores alternativos
        if not amenity_buttons:
            log("No se encontraron botones por role='checkbox', intentando buscar por labels...")
            amenity_labels = driver.find_elements(By.XPATH, "//label")
            amenity_buttons = amenity_labels
            if not amenity_buttons:
                log("No se encontraron botones o labels de amenidades. Intentando buscar divs con texto de amenidades...")
                # Intenta buscar divs que podrían contener texto de amenidades
                amenity_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 't13184oc') or contains(@class, 'ta8vzdc')]")
                amenity_buttons = amenity_divs
        
        # Extrae el texto de los botones/elementos
        amenity_options = []
        amenity_elements = []
        
        for button in amenity_buttons:
            try:
                # Intenta obtener el texto del botón directamente
                text = button.text.strip()
                
                # Si no hay texto, busca dentro del botón por divs con texto
                if not text:
                    inner_divs = button.find_elements(By.XPATH, ".//div")
                    for div in inner_divs:
                        div_text = div.text.strip()
                        if div_text:
                            text = div_text
                            break
                
                if text:
                    amenity_options.append(text)
                    amenity_elements.append(button)
            except Exception as e:
                log(f"Error al extraer texto de un elemento: {e}")
        
        log(f"Texto de amenidades extraído de la UI: {amenity_options}")
        
        # Si no hay opciones en la UI, guarda el HTML para depuración
        if not amenity_options:
            log('No se encontraron textos de amenidades en la UI. Guardando HTML para depuración.')
            with open('debug_amenities.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            driver.save_screenshot('error_no_amenidades.png')
        
        # Normaliza las opciones de la UI
        amenity_options_norm = [normalize(opt) for opt in amenity_options]
        log(f"Amenidades en la UI (normalizadas): {amenity_options_norm}")
        
        # Matching directo y por equivalencia (prioriza coincidencias exactas)
        matches = []
        matched_indices = []
        
        # 1. Primero busca coincidencias exactas
        for i, (opt, opt_norm) in enumerate(zip(amenity_options, amenity_options_norm)):
            if opt_norm in amenities_db_norm:
                matches.append(opt)
                matched_indices.append(i)
                log(f"Coincidencia exacta: '{opt}'")
        
        # 2. Luego busca coincidencias parciales
        for i, (opt, opt_norm) in enumerate(zip(amenity_options, amenity_options_norm)):
            if i not in matched_indices:
                for db_amenity in amenities_db_norm:
                    # Coincidencia si la amenidad de la DB está en el texto de la UI o viceversa
                    if db_amenity in opt_norm or opt_norm in db_amenity:
                        matches.append(opt)
                        matched_indices.append(i)
                        log(f"Coincidencia parcial: '{opt}' con '{db_amenity}'")
                        break
        
        log(f"Amenidades seleccionadas por matching local: {matches}")
        
        # Si hay matches, selecciona en la UI
        seleccionadas = 0
        for i, (element, opt) in enumerate(zip(amenity_elements, amenity_options)):
            if opt in matches:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.3)  # Espera un poco más para scroll
                    
                    # Verifica si ya está seleccionado (aria-checked="true")
                    is_checked = element.get_attribute("aria-checked") == "true"
                    if is_checked:
                        log(f"Amenidad '{opt}' ya está seleccionada")
                        seleccionadas += 1
                        continue
                    
                    # Intenta click normal
                    try:
                        element.click()
                    except Exception as click_error:
                        log(f"Click normal falló, intentando con JavaScript: {click_error}")
                        driver.execute_script("arguments[0].click();", element)
                    
                    log(f"Amenidad seleccionada por matching local: '{opt}'")
                    seleccionadas += 1
                    time.sleep(0.2)  # Pequeña pausa entre clics
                except Exception as e:
                    log(f"No se pudo seleccionar amenidad '{opt}': {e}")
        
        log(f"Total de amenidades seleccionadas por matching local: {seleccionadas}/{len(matches)}")
        if seleccionadas == 0 and amenity_options:
            log("No se seleccionó ninguna amenidad por matching local. Se intentará con Gemini si está configurado.")
        elif seleccionadas < len(matches) * 0.5 and amenity_options:  # Si seleccionó menos del 50% de los matches
            log("Se seleccionaron pocas amenidades. Se complementará con Gemini para mejorar el matching.")
        time.sleep(1)        # SOLO llamar a Gemini si:
        # 1. Hay opciones en la UI
        # 2. No se seleccionaron amenidades localmente, o se seleccionaron muy pocas
        if amenity_options and (seleccionadas == 0 or seleccionadas < len(matches) * 0.5):
            log("Iniciando proceso de selección con Gemini debido a pocas coincidencias locales...")
            GEMINI_API_KEY = 'AIzaSyDkxQbKk0k7N63PU02XDOhW4Q0mb2yUC54'  # <-- Cambia esto por tu API KEY
            GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY
            
            # Mejor prompt con instrucciones claras
            prompt = (
                "Eres un asistente especializado en mapear amenidades de hoteles. "
                "Tu tarea es identificar qué amenidades de la UI de Airbnb corresponden a las amenidades de la base de datos. "
                "Debes ser flexible y considerar sinónimos, variaciones y relaciones semánticas.\n\n"
                "Instrucciones:\n"
                "1. Analiza cuidadosamente cada amenidad de la base de datos\n"
                "2. Compara con las opciones disponibles en la UI\n"
                "3. Devuelve ÚNICAMENTE una lista JSON con los textos EXACTOS de la UI que coinciden\n\n"
                f"Amenidades de la base de datos: {amenities_db}\n"
                f"Opciones disponibles en la UI: {amenity_options}\n\n"
                "Importante: Responde solamente con la lista JSON, sin texto adicional."
            )
            
            headers = {"Content-Type": "application/json"}
            data = pyjson.dumps({
                "contents": [{"parts": [{"text": prompt}]}]
            })
            log("Prompt enviado a Gemini:")
            log(prompt)
            
            # Primer intento
            response = requests.post(GEMINI_URL, headers=headers, data=data)
            log(f"Status Gemini: {response.status_code}")
            if response.status_code != 200:
                log(f"Error al llamar a Gemini: {response.text}")
                log("Continuando sin selección de amenidades por IA")
            else:
                result = response.json()
                log(f"Respuesta cruda de Gemini: {result}")
                
                # Extraer la lista JSON de la respuesta con mejor manejo
                import re
                import ast
                import json
                
                gemini_matches = []
                try:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    log(f"Texto de comparación Gemini: {text}")
                    
                    # Intenta múltiples estrategias para extraer la lista JSON
                    # 1. Buscar patrón de corchetes con regex
                    match = re.search(r'\[(.*?)\]', text, re.DOTALL)
                    if match:
                        try:
                            gemini_matches = ast.literal_eval('[' + match.group(1) + ']')
                        except:
                            # 2. Intentar con json.loads si el regex falla
                            try:
                                # Limpiar el texto para encontrar JSON válido
                                clean_text = re.search(r'(\[.*?\])', text.replace('```json', '').replace('```', ''), re.DOTALL)
                                if clean_text:
                                    gemini_matches = json.loads(clean_text.group(1))
                            except:
                                log("No se pudo parsear respuesta JSON de Gemini")
                except Exception as e:
                    log(f"Error extrayendo matches de Gemini: {e}")
                
                log(f"Amenidades seleccionadas por Gemini: {gemini_matches}")

                # Reintentar la consulta a Gemini si no devuelve matches
                max_retries = 3
                retry = 0
                while retry < max_retries and not gemini_matches:
                    log(f"Reintentando consulta a Gemini ({retry+1}/{max_retries})...")
                    response = requests.post(GEMINI_URL, headers=headers, data=data)
                    log(f"Intento {retry+1} - Status Gemini: {response.status_code}")
                    if response.status_code != 200:
                        log(f"Error al llamar a Gemini: {response.text}")
                        retry += 1
                        time.sleep(2)
                        continue
                    
                    result = response.json()
                    log(f"Intento {retry+1} - Respuesta: {result}")
                    
                    try:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        log(f"Intento {retry+1} - Texto: {text}")
                        
                        # Mismo proceso de extracción que antes
                        match = re.search(r'\[(.*?)\]', text, re.DOTALL)
                        if match:
                            try:
                                gemini_matches = ast.literal_eval('[' + match.group(1) + ']')
                            except:
                                clean_text = re.search(r'(\[.*?\])', text.replace('```json', '').replace('```', ''), re.DOTALL)
                                if clean_text:
                                    gemini_matches = json.loads(clean_text.group(1))
                    except Exception as e:
                        log(f"Intento {retry+1} - Error: {e}")
                    
                    log(f"Intento {retry+1} - Matches: {gemini_matches}")
                    if gemini_matches:
                        break
                    retry += 1
                    time.sleep(2)
                
                # Seleccionar en la UI los que Gemini indicó
                if gemini_matches:
                    log("Procediendo a seleccionar amenidades según Gemini...")
                    seleccionadas_ia = 0
                    for i, (element, opt) in enumerate(zip(amenity_elements, amenity_options)):
                        if opt in gemini_matches and opt not in matches:  # Solo selecciona las que no están ya seleccionadas
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.3)
                                
                                # Verifica si ya está seleccionado
                                is_checked = element.get_attribute("aria-checked") == "true"
                                if is_checked:
                                    log(f"Amenidad '{opt}' ya está seleccionada por IA")
                                    seleccionadas_ia += 1
                                    continue
                                
                                # Intenta click normal y fallback a JavaScript
                                try:
                                    element.click()
                                except:
                                    driver.execute_script("arguments[0].click();", element)
                                
                                log(f"Amenidad seleccionada por IA: '{opt}'")
                                seleccionadas_ia += 1
                                time.sleep(0.2)
                            except Exception as e:
                                log(f"No se pudo seleccionar amenidad '{opt}' por IA: {e}")
                    
                    log(f"Total de amenidades seleccionadas por IA: {seleccionadas_ia}")
                    log(f"Total general de amenidades seleccionadas: {seleccionadas + seleccionadas_ia}")
                    if seleccionadas_ia == 0:
                        log("La IA no pudo seleccionar ninguna amenidad adicional.")
                else:
                    log("Gemini no identificó coincidencias. No se seleccionaron amenidades adicionales.")
            
            time.sleep(1)
    except Exception as e:
        log(f"Error al seleccionar amenidades con Gemini: {e}")
        driver.save_screenshot('error_amenidades.png')
        raise
    # --- Fin selección de amenidades con IA ---

    # --- Selección forzada de amenidades de seguridad ---
    forced_safety = ['detector de humo', 'botiquin', 'extintor', 'extintor de incendios']
    for i, (element, opt, opt_norm) in enumerate(zip(amenity_elements, amenity_options, amenity_options_norm)):
        for forced in forced_safety:
            if forced in opt_norm and opt not in matches:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.3)
                    is_checked = element.get_attribute("aria-checked") == "true"
                    if not is_checked:
                        try:
                            element.click()
                        except Exception as click_error:
                            log(f"Click normal falló en seguridad, intentando con JavaScript: {click_error}")
                            driver.execute_script("arguments[0].click();", element)
                        log(f"Amenidad de seguridad seleccionada forzada: '{opt}'")
                        seleccionadas += 1
                        matches.append(opt)
                        matched_indices.append(i)
                    else:
                        log(f"Amenidad de seguridad '{opt}' ya estaba seleccionada")
                except Exception as e:
                    log(f"No se pudo seleccionar amenidad de seguridad '{opt}': {e}")
    # --- Fin selección forzada de amenidades de seguridad ---

    log(f"Total de amenidades seleccionadas por matching local (incluyendo seguridad): {seleccionadas}/{len(matches)}")
    
    # --- Click final en Siguiente para completar el anuncio ---
    try:
        siguiente_final_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_final_btn)
        time.sleep(0.5)
        siguiente_final_btn.click()
        log("Click en 'Siguiente' final para completar anuncio OK")
        time.sleep(5)  # Esperar a que procese el siguiente paso
    except Exception as e:
        log(f"Error al hacer click en 'Siguiente' final: {e}")
        driver.save_screenshot('error_siguiente_final.png')
        raise
    # --- Fin proceso creación de anuncio ---
    
except Exception as e:
    log(f"Error al automatizar el flujo de creación de anuncio: {e}")
    driver.save_screenshot('error_crear_anuncio.png')
    log("Se guardó una captura de pantalla como error_crear_anuncio.png")
    driver.quit()
    exit(1)

# --- Subida automática de imágenes tras amenidades (usando rutas desde la base de datos) ---
try:
    # Espera a que aparezca el botón 'Agrega fotos' y haz click
    agrega_fotos_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Agrega fotos')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", agrega_fotos_btn)
    time.sleep(0.5)
    agrega_fotos_btn.click()
    log("Click en 'Agrega fotos' OK")
    time.sleep(2)

    # Espera el input file (puede estar oculto, pero Selenium lo encuentra)
    input_file = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))

    # IMPLEMENTACIÓN: Subida de imágenes desde la base de datos (tabla imagen, columna local_path)
    try:
        import sqlite3
        db = sqlite3.connect('hoteles.db')
        c = db.cursor()
        c.execute('SELECT local_path FROM imagen ORDER BY id DESC LIMIT 15')
        imagenes = [row[0] for row in c.fetchall() if row[0] and os.path.exists(row[0])]
        db.close()
        if not imagenes:
            log('No se encontraron imágenes para subir desde la base de datos (tabla imagen)')
        else:
            # Convertir rutas relativas a absolutas para Selenium
            imagenes = [os.path.abspath(img) for img in imagenes]
            input_file.send_keys("\n".join(imagenes))
            log(f"Imágenes subidas desde base de datos: {imagenes}")
            time.sleep(5) # Espera a que se suban las imágenes
    except Exception as e:
        log(f"Error al subir imágenes desde la base de datos: {e}")
        # No hacer raise, solo loggear
        pass
    # --- Fin implementación subida imágenes desde DB ---

    # Click en el botón 'Subir' después de cargar las imágenes
    subir_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Subir')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", subir_btn)
    time.sleep(0.5)
    subir_btn.click()
    log("Click en 'Subir' OK")
    time.sleep(3)
except Exception as e:
    log(f"Error al subir imágenes: {e}")
    driver.save_screenshot('error_subir_imagenes.png')
    raise
# --- Fin subida automática de imágenes ---

# --- Esperar a que termine la subida de fotos y dar click en Siguiente ---
try:
    # Esperar a que desaparezca el loader/spinner de subida o aparezcan los thumbnails de las imágenes
    # Estrategia 1: Esperar a que aparezcan miniaturas de las imágenes subidas
    thumbnails_xpath = "//img[contains(@src, 'data:image') or contains(@src, 'media')]"
    wait.until(lambda d: len(d.find_elements(By.XPATH, thumbnails_xpath)) >= len(imagenes))
    log("Miniaturas de imágenes detectadas, subida finalizada.")
except Exception as e:
    log(f"No se detectaron miniaturas, esperando 10 segundos extra por seguridad: {e}")
    time.sleep(10)

# Click en el botón 'Siguiente' después de subir fotos
try:
    siguiente_fotos_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_fotos_btn)
    time.sleep(0.5)
    siguiente_fotos_btn.click()
    log("Click en 'Siguiente' después de subir fotos OK")
    time.sleep(3)
except Exception as e:
    log(f"Error al hacer click en 'Siguiente' después de fotos: {e}")
    driver.save_screenshot('error_siguiente_fotos.png')
    raise

# --- Generar título con Gemini a partir del nombre y descripción del hotel ---
try:
    import sqlite3
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    c.execute('SELECT nombre, descripcion FROM hotel ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    db.close()
    nombre_hotel = row[0] if row and row[0] else ''
    descripcion_hotel = row[1] if row and row[1] else ''
    if not nombre_hotel and not descripcion_hotel:
        log('No se encontró nombre ni descripción del hotel en la base de datos.')
        raise Exception('No hay datos para generar el título.')
    import requests
    import json as pyjson
    GEMINI_API_KEY = 'AIzaSyDkxQbKk0k7N63PU02XDOhW4Q0mb2yUC54'  # <-- Cambia esto por tu API KEY
    GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY
    prompt = (
        "Eres un experto en generar títulos atractivos para listados de Airbnb. Tu estilo es conciso, evoca sensaciones de lujo, exclusividad, privacidad o refugio, e incluye la ubicación si es relevante. Los títulos deben ser siempre menores a 32 caracteres. Basándote en estos ejemplos:\n\n"
        "'Lujo y exclusividad en Reforma'\n"
        "'Oasis privado'\n"
        "'Oasis privado en Acapulco'\n"
        "'Refugio privado en Mazatlán'\n"
        "'Rincón de Armonía en Acapulco'\n"
        "'Templo de lujo y relajación'\n"
        "'Oasis exclusivo en Veracruz'\n\n"
        "Genera un título para un Airbnb basado en la siguiente información:\n"
        f"Nombre del hotel: {nombre_hotel}\n"
        f"Descripción: {descripcion_hotel}\n"
        "Devuelve solamente el título sin comillas, explicaciones o texto adicional."
    )
    headers = {"Content-Type": "application/json"}
    data = pyjson.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    })
    log("Prompt enviado a Gemini para título:")
    log(prompt)
    response = requests.post(GEMINI_URL, headers=headers, data=data)
    if response.status_code != 200:
        log(f"Error al llamar a Gemini para título: {response.text}")
        raise Exception('Gemini API error para título')
    result = response.json()
    titulo_generado = ''
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        # Limita el título a 32 caracteres (sin cortar palabras si es posible)
        raw_title = text.strip().replace('"', '').replace("'", '')
        if len(raw_title) > 32:
            # Intenta cortar en el último espacio antes de 32
            corte = raw_title[:32].rfind(' ')
            if corte > 20:
                titulo_generado = raw_title[:corte].strip()
            else:
                titulo_generado = raw_title[:32].strip()
        else:
            titulo_generado = raw_title
    except Exception as e:
        log(f"Error extrayendo título de Gemini: {e}")
    log(f"Título generado por Gemini (<=32 chars): {titulo_generado}")
    # Aquí puedes automatizar el llenado del input de título si lo deseas:
    try:
        titulo_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='title' or @placeholder][@type='text']")))
        titulo_input.clear()
        titulo_input.send_keys(titulo_generado)
        log("Título pegado en el input de Airbnb.")
    except Exception as e:
        log(f"No se pudo pegar el título en el input: {e}")
except Exception as e:
    log(f"Error generando título con Gemini: {e}")
    driver.save_screenshot('error_titulo_gemini.png')
    raise
# --- Fin generación de título con Gemini ---

# --- Introducir título generado en el textarea y continuar ---
try:
    # Esperar el textarea por id
    titulo_textarea = wait.until(EC.element_to_be_clickable((By.XPATH, "//textarea[@id='title.title']")))
    titulo_textarea.clear()
    titulo_textarea.send_keys(titulo_generado)
    log("Título pegado en el textarea de Airbnb.")
    time.sleep(1)
    # Click en Siguiente
    siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
    time.sleep(0.5)
    siguiente_btn.click()
    log("Click en 'Siguiente' después del título OK")
    time.sleep(3)
except Exception as e:
    log(f"Error al pegar el título en el textarea o hacer click en Siguiente: {e}")
    driver.save_screenshot('error_titulo_textarea.png')
    raise
# --- Fin título en textarea y siguiente ---

# --- Selección de categoría usando Gemini (solo 2 opciones de 6) ---
try:
    # Opciones de categoría visibles en la UI
    categoria_opciones = [
        'Tranquilo', 'Excepcional', 'Familiar', 'Elegante', 'Central', 'Espacioso'
    ]
    # Buscar los botones de categoría por role=checkbox y extraer texto
    categoria_buttons = driver.find_elements(By.XPATH, "//button[@role='checkbox']")
    categoria_texts = []
    for btn in categoria_buttons:
        try:
            text = btn.text.strip()
            if text in categoria_opciones:
                categoria_texts.append(text)
        except:
            pass
    log(f"Opciones de categoría encontradas: {categoria_texts}")
    # Prompt para Gemini
    prompt_cat = (
        "Eres un experto en marketing de Airbnb. "
        "Elige solo 2 categorías de la siguiente lista que mejor describan el alojamiento, "
        "basándote en el nombre y la descripción del hotel. "
        "Opciones: Tranquilo, Excepcional, Familiar, Elegante, Central, Espacioso. "
        "Devuelve solo una lista JSON con los 2 nombres exactos elegidos, sin texto adicional.\n"
        f"Nombre: {nombre_hotel}\nDescripción: {descripcion_hotel}"
    )
    headers = {"Content-Type": "application/json"}
    data = pyjson.dumps({
        "contents": [{"parts": [{"text": prompt_cat}]}]
    })
    log("Prompt enviado a Gemini para categoría:")
    log(prompt_cat)
    response = requests.post(GEMINI_URL, headers=headers, data=data)
    if response.status_code != 200:
        log(f"Error al llamar a Gemini para categoría: {response.text}")
        raise Exception('Gemini API error para categoría')
    result = response.json()
    categorias_gemini = []
    try:
        import re, ast, json
        text = result['candidates'][0]['content']['parts'][0]['text']
        match = re.search(r'\[(.*?)\]', text, re.DOTALL)
        if match:
            try:
                categorias_gemini = ast.literal_eval('[' + match.group(1) + ']')
            except:
                clean_text = re.search(r'(\[.*?\])', text.replace('```json', '').replace('```', ''), re.DOTALL)
                if clean_text:
                    categorias_gemini = json.loads(clean_text.group(1))
    except Exception as e:
        log(f"Error extrayendo categorías de Gemini: {e}")
    log(f"Categorías seleccionadas por Gemini: {categorias_gemini}")
    # Hacer click en las 2 opciones elegidas
    seleccionadas = 0
    for btn in categoria_buttons:
        try:
            text = btn.text.strip()
            if text in categorias_gemini:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.3)
                is_checked = btn.get_attribute("aria-checked") == "true"
                if not is_checked:
                    btn.click()
                    log(f"Categoría seleccionada: {text}")
                    seleccionadas += 1
                else:
                    log(f"Categoría '{text}' ya estaba seleccionada")
        except Exception as e:
            log(f"No se pudo seleccionar categoría '{text}': {e}")
    log(f"Total de categorías seleccionadas: {seleccionadas}/2")
    time.sleep(1)
    # Click en Siguiente para continuar
    siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
    time.sleep(0.5)
    siguiente_btn.click()
    log("Click en 'Siguiente' después de categorías OK")
    time.sleep(3)
except Exception as e:
    log(f"Error en la selección de categorías con Gemini: {e}")
    driver.save_screenshot('error_categoria_gemini.png')
    raise
# --- Fin selección de categoría con Gemini ---

# --- Generar y pegar descripción con Gemini (máx 500 caracteres) ---
try:
    prompt_desc = (
        "Eres un experto en marketing de Airbnb. "
        "Genera una descripción atractiva, creativa y profesional para un anuncio de Airbnb en español, usando el nombre y la descripción del hotel. "
        "La descripción debe resaltar lo mejor del alojamiento, su experiencia, ubicación, servicios, etc. No repitas el nombre literal. "
        "Devuelve solo la descripción generada, sin comillas ni texto adicional. Máximo 500 caracteres.\n"
        f"Nombre: {nombre_hotel}\n"
        f"Descripción: {descripcion_hotel}"
    )
    headers = {"Content-Type": "application/json"}
    data = pyjson.dumps({
        "contents": [{"parts": [{"text": prompt_desc}]}]
    })
    log("Prompt enviado a Gemini para descripción:")
    log(prompt_desc)
    response = requests.post(GEMINI_URL, headers=headers, data=data)
    if response.status_code != 200:
        log(f"Error al llamar a Gemini para descripción: {response.text}")
        raise Exception('Gemini API error para descripción')
    result = response.json()
    descripcion_generada = ''
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        raw_desc = text.strip().replace('"', '').replace("'", '')
        if len(raw_desc) > 500:
            corte = raw_desc[:500].rfind(' ')
            if corte > 400:
                descripcion_generada = raw_desc[:corte].strip()
            else:
                descripcion_generada = raw_desc[:500].strip()
        else:
            descripcion_generada = raw_desc
    except Exception as e:
        log(f"Error extrayendo descripción de Gemini: {e}")
    log(f"Descripción generada por Gemini (<=500 chars): {descripcion_generada}")
    # Pegar en el textarea
    desc_textarea = wait.until(EC.element_to_be_clickable((By.XPATH, "//textarea[@id='description.summary']")))
    desc_textarea.clear()
    desc_textarea.send_keys(descripcion_generada)
    log("Descripción pegada en el textarea de Airbnb.")
    time.sleep(1)
    # Click en Siguiente
    siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
    time.sleep(0.5)
    siguiente_btn.click()
    log("Click en 'Siguiente' después de descripción OK")
    time.sleep(2)
    # 5 veces click en Siguiente después de descripción
    for i in range(5):
        siguiente_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and text()='Siguiente']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", siguiente_btn)
        time.sleep(0.5)
        siguiente_btn.click()
        log(f"Click {i+1}/5 en 'Siguiente' después de descripción OK")
        time.sleep(2)
    # Click final en 'Crear anuncio'
    crear_anuncio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Siguiente paso' and (text()='Crear anuncio' or contains(.,'Crear anuncio'))]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", crear_anuncio_btn)
    time.sleep(0.5)
    crear_anuncio_btn.click()
    log("Click en 'Crear anuncio' OK")
    time.sleep(3)
except Exception as e:
    log(f"Error generando o pegando descripción con Gemini: {e}")
    driver.save_screenshot('error_descripcion_gemini.png')
    raise
# --- Fin generación y pegado de descripción con Gemini ---

input("Presiona ENTER para cerrar el navegador...")
driver.quit()
log("Navegador cerrado.")
