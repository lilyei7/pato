#!/usr/bin/env python3
"""
Script de verificación final del sistema refactorizado
Muestra el estado actual de hoteles, imágenes y carpetas
"""

import os
import sqlite3
from collections import defaultdict

def mostrar_estado_sistema():
    """Muestra el estado completo del sistema refactorizado"""
    print("🏨 ESTADO DEL SISTEMA REFACTORIZADO")
    print("=" * 60)
    
    # Verificar base de datos
    if not os.path.exists('hoteles.db'):
        print("❌ No se encontró la base de datos hoteles.db")
        return
    
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    
    # Verificar tablas
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    
    if 'hotel' not in tables:
        print("❌ No se encontró la tabla 'hotel'")
        return
    
    # Obtener estadísticas generales
    c.execute("SELECT COUNT(*) FROM hotel")
    total_hoteles = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM imagen") 
    total_imagenes = c.fetchone()[0]
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"  - Total de hoteles: {total_hoteles}")
    print(f"  - Total de imágenes: {total_imagenes}")
    
    # Verificar estructura de carpetas
    print(f"\n📁 ESTRUCTURA DE CARPETAS:")
    
    if not os.path.exists('imagenes'):
        print("  ❌ No existe la carpeta 'imagenes'")
        return
    
    hotel_folders = []
    imagenes_sueltas = 0
    
    for item in os.listdir('imagenes'):
        item_path = os.path.join('imagenes', item)
        if os.path.isdir(item_path) and item.startswith('hotel_'):
            hotel_folders.append(item)
        elif os.path.isfile(item_path) and item.endswith(('.jpg', '.jpeg', '.png')):
            imagenes_sueltas += 1
    
    print(f"  - Carpetas de hotel: {len(hotel_folders)}")
    print(f"  - Imágenes sueltas: {imagenes_sueltas}")
    
    # Detalles por hotel
    print(f"\n🏨 DETALLES POR HOTEL:")
    
    c.execute("""
        SELECT h.id, h.nombre, COUNT(i.id) as num_imagenes 
        FROM hotel h 
        LEFT JOIN imagen i ON h.id = i.hotel_id 
        GROUP BY h.id, h.nombre
        ORDER BY h.id
    """)
    
    for row in c.fetchall():
        hotel_id, nombre, num_imagenes = row
        
        # Buscar carpeta correspondiente
        carpeta_encontrada = None
        for folder in hotel_folders:
            if folder.startswith(f'hotel_{hotel_id}_'):
                carpeta_encontrada = folder
                break
        
        # Contar archivos físicos en la carpeta
        imagenes_fisicas = 0
        if carpeta_encontrada:
            folder_path = os.path.join('imagenes', carpeta_encontrada)
            if os.path.exists(folder_path):
                imagenes_fisicas = len([f for f in os.listdir(folder_path) 
                                     if f.endswith(('.jpg', '.jpeg', '.png'))])
        
        # Mostrar información
        nombre_corto = (nombre[:40] + "...") if nombre and len(nombre) > 40 else (nombre or "Sin nombre")
        status_carpeta = "✓" if carpeta_encontrada else "❌"
        status_imagenes = "✓" if num_imagenes == imagenes_fisicas else "⚠️"
        
        print(f"  {status_carpeta} Hotel {hotel_id}: {nombre_corto}")
        print(f"    - Imágenes en BD: {num_imagenes}")
        print(f"    - Imágenes físicas: {imagenes_fisicas} {status_imagenes}")
        if carpeta_encontrada:
            print(f"    - Carpeta: {carpeta_encontrada}")
        print()
    
    # Verificar integridad de rutas
    print(f"🔍 VERIFICACIÓN DE INTEGRIDAD:")
    
    c.execute("SELECT local_path FROM imagen")
    rutas_bd = [row[0] for row in c.fetchall()]
    
    rutas_existentes = 0
    rutas_faltantes = 0
    rutas_con_carpeta_hotel = 0
    
    for ruta in rutas_bd:
        if os.path.exists(ruta):
            rutas_existentes += 1
            if '\\hotel_' in ruta or '/hotel_' in ruta:
                rutas_con_carpeta_hotel += 1
        else:
            rutas_faltantes += 1
    
    print(f"  - Rutas existentes: {rutas_existentes}/{len(rutas_bd)}")
    print(f"  - Rutas faltantes: {rutas_faltantes}")
    print(f"  - Rutas con carpeta específica: {rutas_con_carpeta_hotel}")
    
    # Estado del sistema
    print(f"\n🎯 ESTADO DEL SISTEMA:")
    if imagenes_sueltas == 0 and rutas_faltantes == 0 and rutas_con_carpeta_hotel == len(rutas_bd):
        print("  🎉 ¡PERFECTO! Todas las imágenes están organizadas por hotel.")
    elif rutas_con_carpeta_hotel > 0:
        print("  ✅ Sistema funcionando - Imágenes nuevas se organizan por hotel.")
        if imagenes_sueltas > 0:
            print(f"  ⚠️  Quedan {imagenes_sueltas} imágenes sin organizar de versiones anteriores.")
    else:
        print("  ❌ Sistema requiere configuración.")
    
    db.close()

def mostrar_ejemplos_rutas():
    """Muestra ejemplos de rutas de imágenes para verificar el formato"""
    print(f"\n📄 EJEMPLOS DE RUTAS:")
    
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    
    c.execute("SELECT hotel_id, local_path FROM imagen LIMIT 8")
    for row in c.fetchall():
        hotel_id, ruta = row
        existe = "✓" if os.path.exists(ruta) else "❌"
        print(f"  {existe} Hotel {hotel_id}: {ruta}")
    
    db.close()

def main():
    """Función principal"""
    mostrar_estado_sistema()
    mostrar_ejemplos_rutas()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
