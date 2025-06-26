import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# Configura el path al geckodriver y Firefox
service = Service("./geckodriver.exe")
options = Options()
options.headless = False  # Para ver el resultado visualmente
options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"

def log(msg):
    print(f"[LOG] {msg}")

# URL de dashboard de anfitrión
dashboard_url = "https://www.airbnb.com/hosting/listings"

log("Abriendo navegador para comprobar sesión con cookies guardadas...")
driver = webdriver.Firefox(service=service, options=options)
driver.get("https://www.airbnb.com/")

# Cargar cookies guardadas
try:
    with open("cookies_airbnb.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        # Selenium requiere que no haya 'sameSite' en el dict
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
time.sleep(5)

# Comprobar si la sesión está activa (buscando el menú de anfitrión o el nombre de usuario)
try:
    # Ejemplo: buscar el menú de "Alojamientos" o "Anfitrión"
    menu = driver.find_elements(By.XPATH, "//*[contains(text(), 'Alojamientos') or contains(text(), 'Hosting') or contains(text(), 'Anfitrión')]")
    if menu:
        log("¡Sesión activa! Se detectó el menú de anfitrión.")
    else:
        log("No se detectó el menú de anfitrión. Puede que la sesión NO esté activa.")
except Exception as e:
    log(f"ERROR al verificar la sesión: {e}")

input("Presiona ENTER para cerrar el navegador...")
driver.quit()
log("Navegador cerrado.")
