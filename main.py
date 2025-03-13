import sqlite3
import pandas as pd
import json

# Leer datos del archivo JSON
with open('datos.json', 'r') as file:
    datos = json.load(file)

print(datos)
print(datos["tickets_emitidos"])

# Conectar a la base de datos SQLite
con = sqlite3.connect('datos.db')
cur = con.cursor()

# Crear tablas en la base de datos
cur.execute('''
CREATE TABLE IF NOT EXISTS Incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    fecha_apertura TEXT,
    fecha_cierre TEXT,
    es_mantenimiento BOOLEAN,
    satisfaccion_cliente INTEGER,
    tipo_incidencia INTEGER
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Contactos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incidente_id INTEGER,
    id_emp TEXT,
    fecha TEXT,
    tiempo REAL,
    FOREIGN KEY (incidente_id) REFERENCES Incidentes (id)
)
''')
con.commit()

#dd