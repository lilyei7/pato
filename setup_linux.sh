#!/bin/bash

# Script de configuración para entorno Linux
echo "===== Configurando el entorno para la automatización de Airbnb/Booking en Linux ====="

# Verificar Python
echo "Verificando instalación de Python..."
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo "✅ Python instalado: $python_version"
else
    echo "❌ Python3 no encontrado. Por favor instale Python 3.8 o superior:"
    echo "sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Crear entorno virtual
echo "Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

# Verificar Firefox
echo "Verificando instalación de Firefox..."
if command -v firefox &>/dev/null; then
    firefox_version=$(firefox --version)
    echo "✅ Firefox instalado: $firefox_version"
else
    echo "❌ Firefox no encontrado. Por favor instale Firefox o Firefox Developer Edition:"
    echo "sudo apt update && sudo apt install firefox"
    # O para Firefox Developer Edition usar PPA o descargar desde Mozilla
fi

# Descargar geckodriver si no existe
if [ ! -f "./geckodriver" ]; then
    echo "Descargando geckodriver..."
    # Determinar arquitectura
    ARCH=$(uname -m)
    if [ "$ARCH" == "x86_64" ]; then
        GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz"
    else
        GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux32.tar.gz"
    fi
    
    wget -q $GECKO_URL -O geckodriver.tar.gz
    tar -xzf geckodriver.tar.gz
    rm geckodriver.tar.gz
    chmod +x geckodriver
    echo "✅ Geckodriver descargado y configurado"
else
    echo "✅ Geckodriver ya existe"
    # Asegurar que tenga permisos de ejecución
    chmod +x geckodriver
fi

# Verificar la base de datos SQLite
echo "Verificando base de datos SQLite..."
if [ -f "hoteles.db" ]; then
    echo "✅ Base de datos hoteles.db encontrada"
else
    echo "⚠️ No se encontró la base de datos hoteles.db. Se creará una nueva al ejecutar el script."
fi

# Verificar cookies
echo "Verificando archivo de cookies..."
if [ -f "cookies_airbnb.json" ]; then
    echo "✅ Archivo de cookies encontrado"
else
    echo "⚠️ No se encontró el archivo cookies_airbnb.json. Deberá iniciar sesión manualmente."
fi

# Crear directorio para imágenes si no existe
echo "Verificando directorio para imágenes..."
if [ ! -d "imagenes" ]; then
    mkdir -p imagenes
    echo "✅ Directorio 'imagenes' creado"
else
    echo "✅ Directorio 'imagenes' ya existe"
fi

echo ""
echo "===== Configuración completada ====="
echo "Para ejecutar el scraper de Booking: python3 scrape_booking.py"
echo "Para ejecutar la automatización de Airbnb: python3 airbnb_crear_anuncio.py"
echo "Recuerde activar el entorno virtual antes: source venv/bin/activate"
echo ""
