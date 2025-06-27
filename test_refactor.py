#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema refactorizado de carpetas por hotel
"""

import os
import sqlite3
import shutil
from scrape_booking import scrape_hotel_full, adaptar_url_mexico

def limpiar_datos_previos():
    """Limpia datos previos para empezar la prueba desde cero"""
    print("=== LIMPIANDO DATOS PREVIOS ===")
    
    # Hacer backup de la base de datos actual
    if os.path.exists('hoteles.db'):
        shutil.copy2('hoteles.db', 'hoteles_backup.db')
        print("✓ Backup de base de datos creado: hoteles_backup.db")
    
    # Crear nueva base de datos limpia
    if os.path.exists('hoteles.db'):
        os.remove('hoteles.db')
        print("✓ Base de datos anterior eliminada")
    
    # Limpiar carpeta de imágenes (opcional, comentar si quieres mantener)
    # if os.path.exists('imagenes'):
    #     shutil.rmtree('imagenes')
    #     print("✓ Carpeta de imágenes eliminada")
    
    print("✓ Limpieza completada\n")

def verificar_estructura_carpetas():
    """Verifica que las carpetas se hayan creado correctamente"""
    print("=== VERIFICANDO ESTRUCTURA DE CARPETAS ===")
    
    if not os.path.exists('imagenes'):
        print("❌ No existe la carpeta base 'imagenes'")
        return False
    
    # Listar todas las subcarpetas de hotel
    hotel_folders = []
    for item in os.listdir('imagenes'):
        item_path = os.path.join('imagenes', item)
        if os.path.isdir(item_path) and item.startswith('hotel_'):
            hotel_folders.append(item)
    
    print(f"✓ Encontradas {len(hotel_folders)} carpetas de hotel:")
    for folder in hotel_folders:
        folder_path = os.path.join('imagenes', folder)
        img_count = len([f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
        print(f"  - {folder}: {img_count} imágenes")
    
    return len(hotel_folders) > 0

def verificar_base_datos():
    """Verifica que la base de datos tenga la estructura correcta y datos relacionados"""
    print("\n=== VERIFICANDO BASE DE DATOS ===")
    
    if not os.path.exists('hoteles.db'):
        print("❌ No existe la base de datos")
        return False
    
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    
    # Verificar tablas
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    print(f"✓ Tablas encontradas: {tables}")
    
    # Verificar hoteles
    c.execute("SELECT COUNT(*) FROM hotel")
    hotel_count = c.fetchone()[0]
    print(f"✓ Hoteles en la base de datos: {hotel_count}")
    
    # Verificar imágenes
    c.execute("SELECT COUNT(*) FROM imagen")
    imagen_count = c.fetchone()[0]
    print(f"✓ Imágenes en la base de datos: {imagen_count}")
    
    # Verificar relaciones
    c.execute("""
        SELECT h.id, h.nombre, COUNT(i.id) as num_imagenes 
        FROM hotel h 
        LEFT JOIN imagen i ON h.id = i.hotel_id 
        GROUP BY h.id, h.nombre
    """)
    
    print("✓ Relación hoteles-imágenes:")
    total_relacionadas = 0
    for row in c.fetchall():
        hotel_id, nombre, num_imagenes = row
        nombre_corto = nombre[:50] + "..." if len(nombre) > 50 else nombre
        print(f"  - Hotel {hotel_id} ({nombre_corto}): {num_imagenes} imágenes")
        total_relacionadas += num_imagenes
    
    # Verificar que las rutas de imágenes sean correctas
    c.execute("SELECT local_path FROM imagen LIMIT 5")
    print("✓ Ejemplos de rutas de imágenes:")
    for row in c.fetchall():
        ruta = row[0]
        exists = "✓" if os.path.exists(ruta) else "❌"
        print(f"  {exists} {ruta}")
    
    db.close()
    return hotel_count > 0 and imagen_count > 0

def test_single_hotel():
    """Prueba el scraping de un solo hotel"""
    print("\n=== PROBANDO SCRAPING DE UN HOTEL ===")
    
    # URL de prueba
    test_url = "https://www.booking.com/hotel/mx/marriott-tuxtla-gutierrez.es.html?aid=898224&label=hotel_details-SiL4Ie%401750958832&sid=5b9c306f41e272986795b20d3b755e79&checkin=2025-06-26&checkout=2025-06-27&dist=0&from_sn=ios&group_adults=2&group_children=0&keep_landing=1&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA%2C&sb_price_type=total&type=total&"
    
    print(f"Probando con URL: {test_url}")
    
    try:
        url_mexico = adaptar_url_mexico(test_url)
        print(f"URL adaptada: {url_mexico}")
        
        # Ejecutar scraping
        scrape_hotel_full(url_mexico)
        print("✓ Scraping completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en scraping: {str(e)}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA REFACTORIZADO")
    print("=" * 60)
    
    # Paso 1: Limpiar datos previos (opcional)
    # limpiar_datos_previos()
    
    # Paso 2: Probar scraping de un hotel
    success = test_single_hotel()
    
    if success:
        # Paso 3: Verificar estructura de carpetas
        carpetas_ok = verificar_estructura_carpetas()
        
        # Paso 4: Verificar base de datos
        db_ok = verificar_base_datos()
        
        # Resumen
        print("\n" + "=" * 60)
        print("🏁 RESUMEN DE PRUEBAS")
        print(f"✓ Scraping: {'EXITOSO' if success else 'FALLÓ'}")
        print(f"✓ Carpetas: {'CORRECTO' if carpetas_ok else 'FALLÓ'}")
        print(f"✓ Base de datos: {'CORRECTO' if db_ok else 'FALLÓ'}")
        
        if success and carpetas_ok and db_ok:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        else:
            print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
