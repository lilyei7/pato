import sqlite3

# Conectar a la base de datos
db = sqlite3.connect('hoteles.db')
c = db.cursor()

# Mostrar tablas
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = c.fetchall()
print('Tablas:', tables)

if not tables:
    print("❌ La base de datos está vacía o no tiene tablas")
    db.close()
    exit()

# Verificar si existe la tabla hotel
table_names = [table[0] for table in tables]
if 'hotel' not in table_names:
    print("❌ No existe la tabla 'hotel'")
    db.close()
    exit()

# Mostrar estructura de la tabla hotel
c.execute('PRAGMA table_info(hotel)')
print('Estructura hotel:', c.fetchall())

# Mostrar estructura de la tabla imagen si existe
if 'imagen' in table_names:
    c.execute('PRAGMA table_info(imagen)')
    print('Estructura imagen:', c.fetchall())

# Contar registros
c.execute('SELECT COUNT(*) FROM hotel')
print('Hoteles totales:', c.fetchone()[0])

if 'imagen' in table_names:
    c.execute('SELECT COUNT(*) FROM imagen')
    print('Imágenes totales:', c.fetchone()[0])

# Mostrar algunos ejemplos de datos de hotel
c.execute('SELECT id, nombre, direccion FROM hotel LIMIT 3')
print('\nEjemplos de hoteles:')
for row in c.fetchall():
    print(f"ID: {row[0]}, Nombre: {row[1][:50]}..., Dirección: {row[2][:50]}...")

# Mostrar algunos ejemplos de datos de imagen
if 'imagen' in table_names:
    c.execute('SELECT id, hotel_id, local_path FROM imagen LIMIT 5')
    print('\nEjemplos de imágenes:')
    for row in c.fetchall():
        print(f"ID: {row[0]}, Hotel ID: {row[1]}, Path: {row[2]}")

db.close()
