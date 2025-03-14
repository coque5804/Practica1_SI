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

    media_incidentes_cliente = (df_incidentes.groupby('cliente').size().mean())
    desviacion_incidentes_cliente = (df_incidentes.groupby('cliente').size().std())

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

    min_incidentes_empleado = (df_contactos.groupby('id_emp').size().min())
    max_incidentes_empleado = (df_contactos.groupby('id_emp').size().max())

    # Cálculos específicos para la variable "Fraude"
    fraude_incidentes = df_incidentes[df_incidentes['tipo_incidencia'] == 5]  # Asumiendo que 5 representa "Fraude"
    num_incidentes_fraude = len(fraude_incidentes)
    num_actuaciones_fraude = (df_contactos[df_contactos['incidente_id'].isin(fraude_incidentes['id'])].shape[0])/2

    # Análisis estadístico básico
    mediana_fraude = fraude_incidentes['satisfaccion_cliente'].median()
    media_fraude = fraude_incidentes['satisfaccion_cliente'].mean()
    varianza_fraude = fraude_incidentes['satisfaccion_cliente'].var()
    max_fraude = fraude_incidentes['satisfaccion_cliente'].max()
    min_fraude = fraude_incidentes['satisfaccion_cliente'].min()

    # Cerrar conexión
    con.close()

    # Resultados generales
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

    # Resultados específicos para la variable "Fraude"
    resultados_fraude = {
        "num_incidentes_fraude": num_incidentes_fraude,
        "num_actuaciones_fraude": num_actuaciones_fraude,
        "mediana_fraude": mediana_fraude,
        "media_fraude": media_fraude,
        "varianza_fraude": varianza_fraude,
        "max_fraude": max_fraude,
        "min_fraude": min_fraude
    }

    return resultados, resultados_fraude

@app.route('/')
def index():
    resultados, resultados_fraude = obtener_datos()
    return render_template('index.html', resultados=resultados, resultados_fraude=resultados_fraude)

if __name__ == '__main__':
    app.run(debug=True)
