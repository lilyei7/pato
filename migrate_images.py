#!/usr/bin/env python3
"""
Script para migrar las imágenes existentes de la carpeta compartida 
a carpetas específicas por hotel
"""

import os
import sqlite3
import shutil
import re
from collections import defaultdict

def obtener_datos_hoteles():
    """Obtiene los datos de hoteles y sus imágenes desde la base de datos"""
    print("=== OBTENIENDO DATOS DE LA BASE DE DATOS ===")
    
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    
    # Obtener información de hoteles e imágenes
    c.execute("""
        SELECT h.id, h.nombre, i.local_path 
        FROM hotel h 
        LEFT JOIN imagen i ON h.id = i.hotel_id 
        WHERE i.local_path IS NOT NULL AND i.local_path != ''
        ORDER BY h.id
    """)
    
    results = c.fetchall()
    db.close()
    
    # Agrupar por hotel
    hoteles_data = defaultdict(list)
    for hotel_id, hotel_name, image_path in results:
        hoteles_data[hotel_id].append({
            'nombre': hotel_name,
            'imagen_path': image_path
        })
    
    print(f"✓ Encontrados {len(hoteles_data)} hoteles con imágenes")
    return hoteles_data

def limpiar_nombre_hotel(nombre):
    """Limpia el nombre del hotel para usarlo como nombre de carpeta"""
    if not nombre:
        return 'hotel_sin_nombre'
    
    # Eliminar texto de "Ofertas en" y "(Hotel)", etc.
    nombre = re.sub(r'^Ofertas en\s+', '', nombre)
    nombre = re.sub(r'\s*\([^)]*\)\s*', '', nombre)  # Quitar contenido entre paréntesis
    nombre = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', nombre)
    nombre = re.sub(r'[^\w\s-]', '_', nombre)
    nombre = re.sub(r'\s+', '_', nombre)
    nombre = nombre.strip('_')[:50]  # Limitar longitud
    
    return nombre if nombre else 'hotel_sin_nombre'

def crear_carpetas_hoteles(hoteles_data):
    """Crea las carpetas específicas para cada hotel"""
    print("\n=== CREANDO CARPETAS DE HOTELES ===")
    
    if not os.path.exists('imagenes'):
        os.makedirs('imagenes')
    
    carpetas_creadas = {}
    
    for hotel_id, imagenes_info in hoteles_data.items():
        if not imagenes_info:
            continue
            
        # Obtener el nombre del hotel (todos tienen el mismo nombre)
        hotel_name = imagenes_info[0]['nombre']
        clean_name = limpiar_nombre_hotel(hotel_name)
        
        # Crear carpeta del hotel
        hotel_folder = os.path.join('imagenes', f'hotel_{hotel_id}_{clean_name}')
        if not os.path.exists(hotel_folder):
            os.makedirs(hotel_folder)
            print(f"✓ Creada carpeta: {hotel_folder}")
        
        carpetas_creadas[hotel_id] = hotel_folder
    
    return carpetas_creadas

def migrar_imagenes(hoteles_data, carpetas_hoteles):
    """Migra las imágenes desde la carpeta compartida a las carpetas específicas"""
    print("\n=== MIGRANDO IMÁGENES ===")
    
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    
    imagenes_migradas = 0
    imagenes_no_encontradas = 0
    
    for hotel_id, imagenes_info in hoteles_data.items():
        if hotel_id not in carpetas_hoteles:
            continue
            
        hotel_folder = carpetas_hoteles[hotel_id]
        hotel_name = imagenes_info[0]['nombre']
        
        print(f"\nMigrando imágenes del Hotel {hotel_id}: {hotel_name[:50]}...")
        
        for img_info in imagenes_info:
            old_path = img_info['imagen_path']
            
            # Verificar si la imagen existe en la ubicación antigua
            if not os.path.exists(old_path):
                print(f"  ❌ No encontrada: {old_path}")
                imagenes_no_encontradas += 1
                continue
            
            # Si la imagen ya está en una subcarpeta, saltamos
            if '\\hotel_' in old_path or '/hotel_' in old_path:
                print(f"  ⏭️  Ya migrada: {os.path.basename(old_path)}")
                continue
            
            # Generar nueva ruta
            filename = os.path.basename(old_path)
            new_path = os.path.join(hotel_folder, filename)
            
            try:
                # Mover la imagen
                shutil.move(old_path, new_path)
                print(f"  ✓ Migrada: {filename}")
                
                # Actualizar la base de datos con la nueva ruta
                c.execute('UPDATE imagen SET local_path = ? WHERE local_path = ?', 
                         (new_path, old_path))
                
                imagenes_migradas += 1
                
            except Exception as e:
                print(f"  ❌ Error migrando {filename}: {str(e)}")
    
    db.commit()
    db.close()
    
    print(f"\n✓ Imágenes migradas exitosamente: {imagenes_migradas}")
    print(f"❌ Imágenes no encontradas: {imagenes_no_encontradas}")
    
    return imagenes_migradas

def verificar_migracion():
    """Verifica que la migración se haya completado correctamente"""
    print("\n=== VERIFICANDO MIGRACIÓN ===")
    
    # Contar archivos en la carpeta principal
    imagenes_sueltas = 0
    if os.path.exists('imagenes'):
        for item in os.listdir('imagenes'):
            item_path = os.path.join('imagenes', item)
            if os.path.isfile(item_path) and item.endswith(('.jpg', '.jpeg', '.png')):
                imagenes_sueltas += 1
    
    # Contar carpetas de hotel y sus imágenes
    hotel_folders = []
    total_imagenes_organizadas = 0
    
    if os.path.exists('imagenes'):
        for item in os.listdir('imagenes'):
            item_path = os.path.join('imagenes', item)
            if os.path.isdir(item_path) and item.startswith('hotel_'):
                hotel_folders.append(item)
                img_count = len([f for f in os.listdir(item_path) 
                               if f.endswith(('.jpg', '.jpeg', '.png'))])
                total_imagenes_organizadas += img_count
                print(f"  📁 {item}: {img_count} imágenes")
    
    print(f"\n📊 RESUMEN:")
    print(f"  - Imágenes sueltas en /imagenes: {imagenes_sueltas}")
    print(f"  - Carpetas de hotel: {len(hotel_folders)}")
    print(f"  - Imágenes organizadas: {total_imagenes_organizadas}")
    
    if imagenes_sueltas == 0:
        print("🎉 ¡Migración completada! Todas las imágenes están organizadas.")
    else:
        print(f"⚠️  Quedan {imagenes_sueltas} imágenes sin organizar.")

def main():
    """Función principal de migración"""
    print("🔄 INICIANDO MIGRACIÓN DE IMÁGENES A CARPETAS POR HOTEL")
    print("=" * 70)
    
    try:
        # Paso 1: Obtener datos de la base de datos
        hoteles_data = obtener_datos_hoteles()
        
        if not hoteles_data:
            print("❌ No se encontraron hoteles con imágenes para migrar.")
            return
        
        # Paso 2: Crear carpetas para cada hotel
        carpetas_hoteles = crear_carpetas_hoteles(hoteles_data)
        
        # Paso 3: Migrar imágenes
        imagenes_migradas = migrar_imagenes(hoteles_data, carpetas_hoteles)
        
        # Paso 4: Verificar migración
        verificar_migracion()
        
        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")

if __name__ == "__main__":
    main()
