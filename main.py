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

# Insertar datos en las tablas
for ticket in datos["tickets_emitidos"]:
    cur.execute('''
    INSERT INTO Incidentes (cliente, fecha_apertura, fecha_cierre, es_mantenimiento, satisfaccion_cliente, tipo_incidencia)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (ticket['cliente'], ticket['fecha_apertura'], ticket['fecha_cierre'], ticket['es_mantenimiento'],
          ticket['satisfaccion_cliente'], ticket['tipo_incidencia']))

    incidente_id = cur.lastrowid

    for contacto in ticket['contactos_con_empleados']:
        cur.execute('''
        INSERT INTO Contactos (incidente_id, id_emp, fecha, tiempo)
        VALUES (?, ?, ?, ?)
        ''', (incidente_id, contacto['id_emp'], contacto['fecha'], contacto['tiempo']))
    con.commit()

# Realizar consultas y almacenar resultados en DataFrames
df_incidentes = pd.read_sql_query('SELECT * FROM Incidentes', con)
df_contactos = pd.read_sql_query('SELECT * FROM Contactos', con)

# Calcular valores necesarios
num_muestras = len(df_incidentes)
media_valoracion = df_incidentes[df_incidentes['satisfaccion_cliente'] >= 5]['satisfaccion_cliente'].mean()
desviacion_valoracion = df_incidentes[df_incidentes['satisfaccion_cliente'] >= 5]['satisfaccion_cliente'].std()

media_incidentes_cliente = df_incidentes.groupby('cliente').size().mean()
desviacion_incidentes_cliente = df_incidentes.groupby('cliente').size().std()

media_horas_incidente = df_contactos.groupby('incidente_id')['tiempo'].sum().mean()
desviacion_horas_incidente = df_contactos.groupby('incidente_id')['tiempo'].sum().std()

min_horas_empleados = df_contactos['tiempo'].min()
max_horas_empleados = df_contactos['tiempo'].max()

# Convertir fechas a formato datetime
df_incidentes['fecha_apertura'] = pd.to_datetime(df_incidentes['fecha_apertura'], errors='coerce')
df_incidentes['fecha_cierre'] = pd.to_datetime(df_incidentes['fecha_cierre'], errors='coerce')

tiempo_resolucion = (df_incidentes['fecha_cierre'] - df_incidentes['fecha_apertura']).dropna()

# Verificar si hay datos antes de calcular min y max
min_tiempo_incidente = tiempo_resolucion.min().days if not tiempo_resolucion.empty else None
max_tiempo_incidente = tiempo_resolucion.max().days if not tiempo_resolucion.empty else None


min_incidentes_empleado = df_contactos.groupby('id_emp').size().min()
max_incidentes_empleado = df_contactos.groupby('id_emp').size().max()


