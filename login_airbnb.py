import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Configura el path al geckodriver y Firefox
service = Service("./geckodriver.exe")
options = Options()
# NO headless para que puedas loguear manualmente
options.headless = False
options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"

def log(msg):
    print(f"[LOG] {msg}")

# URL de login de Airbnb
login_url = "https://www.airbnb.com/login"

log("Abriendo navegador para login manual en Airbnb...")
driver = webdriver.Firefox(service=service, options=options)
driver.get(login_url)

log("Por favor, inicia sesión manualmente en la ventana abierta.")
log("Cuando termines y veas tu perfil/logueo exitoso, vuelve aquí y presiona ENTER...")
input("Presiona ENTER cuando hayas terminado el login en Airbnb...")

# Ir a la página de gestión de anfitrión (dashboard de anfitrión)
host_dashboard_url = "https://www.airbnb.com/hosting/listings"
log("Navegando a la página de gestión de anfitrión...")
driver.get(host_dashboard_url)
time.sleep(5)  # Esperar a que cargue la página

# Guardar cookies
try:
    cookies = driver.get_cookies()
    with open("cookies_airbnb.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    log(f"Cookies guardadas en cookies_airbnb.json ({len(cookies)} cookies)")
except Exception as e:
    log(f"ERROR al guardar cookies: {e}")
finally:
    driver.quit()
    log("Navegador cerrado. ¡Listo!")
