# Automatización de Booking y Airbnb

Este proyecto automatiza la extracción de datos de hoteles desde Booking.com y la creación de anuncios en Airbnb.

## Estructura del proyecto

- `scrape_booking.py` - Script para extraer datos de hoteles desde Booking.com
- `airbnb_crear_anuncio.py` - Script para crear anuncios automáticamente en Airbnb
- `login_airbnb.py` - Script para iniciar sesión en Airbnb y guardar cookies
- `check_airbnb_session.py` - Script para verificar si la sesión de Airbnb es válida
- `obtener_rutas_imagenes.py` - Herramienta para obtener rutas de imágenes
- `ver_datos.py` - Herramienta para ver los datos extraídos
- `requirements.txt` - Lista de dependencias de Python
- `setup_linux.sh` - Script para configurar el entorno en Linux

## Configuración en Linux

1. **Permisos para ejecutar los scripts**:
   ```bash
   chmod +x setup_linux.sh
   chmod +x geckodriver
   ```

2. **Ejecutar script de configuración**:
   ```bash
   ./setup_linux.sh
   ```

3. **Activar entorno virtual**:
   ```bash
   source venv/bin/activate
   ```

## Uso

1. **Extraer datos de un hotel de Booking**:
   ```bash
   python3 scrape_booking.py
   ```
   Puedes modificar la URL del hotel en el archivo `scrape_booking.py`.

2. **Iniciar sesión en Airbnb** (solo la primera vez):
   ```bash
   python3 login_airbnb.py
   ```

3. **Crear anuncio en Airbnb**:
   ```bash
   python3 airbnb_crear_anuncio.py
   ```

## Posibles problemas en Linux

- **Firefox no encontrado**: Asegúrate de tener Firefox instalado. El script intentará encontrarlo en ubicaciones comunes.
- **Permisos de geckodriver**: Si hay problemas con el geckodriver, asegúrate de que tenga permisos de ejecución.
- **Rutas absolutas**: Si usaste rutas absolutas de Windows en alguna parte del código, deberás actualizarlas.
- **Problemas de visualización**: Si ejecutas en un servidor sin interfaz gráfica, asegúrate de configurar `options.headless = True`.

## Dependencias

- Python 3.8+
- Selenium
- PIL (Pillow)
- Transformers
- Requests
- SQLite3 (incluido en Python)
- Firefox o Firefox Developer Edition
- Geckodriver
