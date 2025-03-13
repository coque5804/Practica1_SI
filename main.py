import sqlite3
import pandas as pd
import json

# Leer datos del archivo JSON
with open('datos.json', 'r') as file:
    data = json.load(file)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('incidentes.db')
cursor = conn.cursor()

#master