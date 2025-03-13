from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__)

def obtener_datos():
    # Conectar a la base de datos SQLite
    con = sqlite3.connect('datos.db')

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

    # Cerrar conexión
    con.close()

    # Resultados
    resultados = {
        "num_muestras": num_muestras,
        "media_valoracion": media_valoracion,
        "desviacion_valoracion": desviacion_valoracion,
        "media_incidentes_cliente": media_incidentes_cliente,
        "desviacion_incidentes_cliente": desviacion_incidentes_cliente,
        "media_horas_incidente": media_horas_incidente,
        "desviacion_horas_incidente": desviacion_horas_incidente,
        "min_horas_empleados": min_horas_empleados,
        "max_horas_empleados": max_horas_empleados,
        "min_tiempo_incidente": min_tiempo_incidente,
        "max_tiempo_incidente": max_tiempo_incidente,
        "min_incidentes_empleado": min_incidentes_empleado,
        "max_incidentes_empleado": max_incidentes_empleado
    }

    return resultados

@app.route('/')
def index():
    resultados = obtener_datos()
    return render_template('index.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)