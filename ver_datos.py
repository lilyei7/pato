import sqlite3

def mostrar_datos():
    db = sqlite3.connect('hoteles.db')
    c = db.cursor()
    
    # Obtener todos los hoteles
    c.execute('SELECT * FROM hotel')
    hoteles = c.fetchall()
    
    if not hoteles:
        print("No hay datos de hoteles en la base de datos.")
        return
    
    for hotel in hoteles:
        print("=" * 60)
        print(f"HOTEL ID: {hotel[0]}")
        print(f"NOMBRE: {hotel[1]}")
        print(f"DIRECCIÓN: {hotel[2]}")
        print(f"PUNTUACIÓN: {hotel[3]}")
        print("-" * 40)
        print(f"DESCRIPCIÓN: {hotel[4]}")
        print("-" * 40)
        print(f"PRECIOS:")
        if hotel[5]:
            for precio in hotel[5].split('\n'):
                print(f"  • {precio}")
        print("-" * 40)
        print(f"AMENITIES:")
        if hotel[6]:
            for amenity in hotel[6].split('\n'):
                print(f"  • {amenity}")
        print("-" * 40)
        print(f"TIPOS DE HABITACIONES:")
        if hotel[7]:
            for habitacion in hotel[7].split('\n'):
                print(f"  • {habitacion}")
          # Obtener imágenes del hotel
        c.execute('SELECT url, local_path FROM imagen WHERE hotel_id = ?', (hotel[0],))
        imagenes = c.fetchall()
        print("-" * 40)
        print(f"IMÁGENES ({len(imagenes)} encontradas):")
        for i, img in enumerate(imagenes[:10], 1):  # Mostrar solo las primeras 10
            url, local_path = img
            if local_path:
                print(f"  {i}. Archivo local: {local_path}")
                print(f"      URL original: {url}")
            else:
                print(f"  {i}. URL: {url}")
        if len(imagenes) > 10:
            print(f"  ... y {len(imagenes) - 10} más")
        
        print("=" * 60)
        print()
    
    db.close()

if __name__ == "__main__":
    mostrar_datos()
