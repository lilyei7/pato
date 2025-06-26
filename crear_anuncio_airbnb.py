import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException

# Configura el path al geckodriver y Firefox
service = Service("./geckodriver.exe")
options = Options()
options.headless = False  # Para ver el proceso
options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"

def log(msg):
    print(f"[LOG] {msg}")

# Datos de ejemplo para el anuncio (puedes cambiarlos)
TITULO = "Departamento moderno en el centro"
DIRECCION = "Calle Falsa 123, Ciudad, País"
TIPO = "Departamento"

# URL para crear un nuevo anuncio
dashboard_url = "https://www.airbnb.com/hosting/listings"
crear_url = "https://www.airbnb.com/rooms/new"

log("Abriendo navegador y cargando cookies...")
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

driver.refresh()
wait = WebDriverWait(driver, 30)

# Esperar a que el menú de anfitrión esté presente
try:
    log("Esperando a que el menú de anfitrión esté visible...")
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Alojamientos') or contains(text(), 'Hosting') or contains(text(), 'Anfitrión')]")))
    log("¡Menú de anfitrión detectado! Esperando 3 segundos extra para asegurar carga completa...")
    time.sleep(3)
except Exception as e:
    log(f"No se detectó el menú de anfitrión: {e}")
    driver.quit()
    exit(1)

# Ahora sí, esperar y hacer clic en 'Agregar anuncio'
try:
    log("Buscando botón 'Agregar anuncio'...")
    add_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Agregar anuncio"]')))
    log("Botón 'Agregar anuncio' visible, haciendo scroll...")
    driver.execute_script("arguments[0].scrollIntoView();", add_btn)
    time.sleep(1)
    log("Intentando clic normal en 'Agregar anuncio'...")
    try:
        add_btn.click()
        log("Clic normal realizado en 'Agregar anuncio'. Esperando 3 segundos...")
    except (ElementClickInterceptedException, WebDriverException) as e:
        log(f"Clic normal falló: {e}. Intentando clic con JavaScript...")
        driver.execute_script("arguments[0].click();", add_btn)
        log("Clic con JavaScript realizado en 'Agregar anuncio'. Esperando 3 segundos...")
    time.sleep(3)
except Exception as e:
    log(f"No se pudo hacer clic en 'Agregar anuncio': {e}")
    driver.save_screenshot('error_agregar_anuncio.png')
    log("Se guardó una captura de pantalla como error_agregar_anuncio.png")
    driver.quit()
    exit(1)

# Paso 2: Esperar y hacer clic en "Casa" (id="homes-card")
try:
    log("Buscando botón 'Casa' (homes-card)...")
    home_btn = wait.until(EC.element_to_be_clickable((By.ID, 'homes-card')))
    log("Botón 'Casa' encontrado, haciendo scroll...")
    driver.execute_script("arguments[0].scrollIntoView();", home_btn)
    time.sleep(1)
    log("Haciendo clic en 'Casa'...")
    home_btn.click()
    log("Clic realizado en 'Casa'. Esperando 3 segundos...")
    time.sleep(3)
except Exception as e:
    log(f"No se pudo hacer clic en 'Casa': {e}")
    driver.quit()
    exit(1)

log("Listo, ya se inició el flujo de creación de anuncio. Puedes continuar manualmente o dime el siguiente paso a automatizar.")
input("Presiona ENTER para cerrar el navegador...")
driver.quit()
log("Navegador cerrado.")
