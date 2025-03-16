from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

def datos():
    conexion = sqlite3.connect('datos.db')

    df_incidentes = pd.read_sql_query('SELECT * FROM Incidentes', conexion)
    df_contactos = pd.read_sql_query('SELECT * FROM Contactos', conexion)

    num_muestras = len(df_incidentes)
    media_valoracion = df_incidentes[df_incidentes['satisfaccion_cliente'] >= 5]['satisfaccion_cliente'].mean()
    desviacion_valoracion = df_incidentes[df_incidentes['satisfaccion_cliente'] >= 5]['satisfaccion_cliente'].std()

    media_incidentes_cliente = (df_incidentes.groupby('cliente').size().mean())
    desviacion_incidentes_cliente = (df_incidentes.groupby('cliente').size().std())

    media_horas_incidente = df_contactos.groupby('incidente_id')['tiempo'].sum().mean()
    desviacion_horas_incidente = df_contactos.groupby('incidente_id')['tiempo'].sum().std()

    min_horas_empleados = df_contactos['tiempo'].min()
    max_horas_empleados = df_contactos['tiempo'].max()

    df_incidentes['fecha_apertura'] = pd.to_datetime(df_incidentes['fecha_apertura'], errors='coerce')
    df_incidentes['fecha_cierre'] = pd.to_datetime(df_incidentes['fecha_cierre'], errors='coerce')

    tiempo_resolucion = (df_incidentes['fecha_cierre'] - df_incidentes['fecha_apertura']).dropna()
    if not tiempo_resolucion.empty:
        min_tiempo_incidente = tiempo_resolucion.min().days
        max_tiempo_incidente = tiempo_resolucion.max().days
    else:
        min_tiempo_incidente = None
        max_tiempo_incidente = None

    min_incidentes_empleado = (df_contactos.groupby('id_emp').size().min())
    max_incidentes_empleado = (df_contactos.groupby('id_emp').size().max())


    fraude_incidentes = df_incidentes[df_incidentes['tipo_incidencia'] == 5]
    num_incidentes_fraude = len(fraude_incidentes)
    num_actuaciones_fraude = (df_contactos[df_contactos['incidente_id'].isin(fraude_incidentes['id'])].shape[0])/2

    mediana_fraude = fraude_incidentes['satisfaccion_cliente'].median()
    media_fraude = fraude_incidentes['satisfaccion_cliente'].mean()
    varianza_fraude = fraude_incidentes['satisfaccion_cliente'].var()
    max_fraude = fraude_incidentes['satisfaccion_cliente'].max()
    min_fraude = fraude_incidentes['satisfaccion_cliente'].min()

    conexion.close()

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

def graficos():
    conexion = sqlite3.connect('datos.db')

    df_incidentes = pd.read_sql_query('SELECT * FROM Incidentes', conexion)
    df_contactos = pd.read_sql_query('SELECT * FROM Contactos', conexion)

    df_incidentes['fecha_apertura'] = pd.to_datetime(df_incidentes['fecha_apertura'], errors='coerce')
    df_incidentes['fecha_cierre'] = pd.to_datetime(df_incidentes['fecha_cierre'], errors='coerce')

    df_incidentes['tiempo_resolucion'] = (df_incidentes['fecha_cierre'] - df_incidentes['fecha_apertura']).dt.days

    media_tiempo_mantenimiento = df_incidentes[df_incidentes['es_mantenimiento'] == True]['tiempo_resolucion'].mean()
    media_tiempo_no_mantenimiento = df_incidentes[df_incidentes['es_mantenimiento'] == False]['tiempo_resolucion'].mean()

    plt.figure(figsize=(10, 5))
    plt.bar(['Mantenimiento', 'No Mantenimiento'], [media_tiempo_mantenimiento, media_tiempo_no_mantenimiento])
    plt.xlabel('Tipo de Incidencia')
    plt.ylabel('Media de Tiempo (días)')
    plt.title('Media de Tiempo de Resolución por Tipo de Incidencia')
    plt.savefig('static/media_tiempo_resolucion.png')

    plt.figure(figsize=(10, 5))
    df_boxplot = df_incidentes[['tipo_incidencia', 'tiempo_resolucion']].copy()

    df_boxplot['tipo_incidencia'] = df_boxplot['tipo_incidencia'].astype(int)
    df_boxplot = df_boxplot.sort_values('tipo_incidencia')

    df_boxplot_incidencia = []
    for tipo in sorted(df_boxplot['tipo_incidencia'].unique()):
        df_boxplot_incidencia.append(df_boxplot[df_boxplot['tipo_incidencia'] == tipo]['tiempo_resolucion'])

    plt.boxplot(df_boxplot_incidencia, labels=sorted(df_boxplot['tipo_incidencia'].unique()), showfliers=False)
    plt.xlabel('Tipo de Incidencia')
    plt.ylabel('Tiempo de Resolución (días)')
    plt.title('Boxplot de Tiempos de Resolución por Tipo de Incidencia')
    plt.savefig('static/boxplot_tiempos_resolucion.png')

    df_criticos = df_incidentes[(df_incidentes['es_mantenimiento'] == True) & (df_incidentes['tipo_incidencia'] != 1)]
    top_5_clientes = df_criticos['cliente'].value_counts().head(5)

    plt.figure(figsize=(10, 5))
    top_5_clientes.plot(kind='bar', color='skyblue')
    plt.xlabel('Cliente')
    plt.ylabel('Número de Incidentes')
    plt.title('Top 5 Clientes Más Críticos')
    plt.savefig('static/top_5_clientes_criticos.png')

    actuaciones_empleado = df_contactos.groupby('id_emp').size()

    plt.figure(figsize=(10, 5))
    actuaciones_empleado.plot(kind='bar', color='orange')
    plt.xlabel('Empleado')
    plt.ylabel('Número de Actuaciones')
    plt.title('Total de Actuaciones por Empleados')
    plt.savefig('static/actuaciones_por_empleados.png')

    df_incidentes['dia_semana'] = df_incidentes['fecha_apertura'].dt.day_name()
    actuaciones_por_dia = df_contactos.merge(df_incidentes[['id', 'dia_semana']], left_on='incidente_id', right_on='id')['dia_semana'].value_counts()

    plt.figure(figsize=(10, 8))
    actuaciones_por_dia.plot(kind='bar', color='green')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Total de Actuaciones')
    plt.title('Actuaciones por Día de la Semana')
    plt.savefig('static/actuaciones_por_dia.png')
    
    conexion.close()

@app.route('/')
def index():
    resultados, resultados_fraude = datos()
    graficos()
    return render_template('index.html', resultados=resultados, resultados_fraude=resultados_fraude)
if __name__ == '__main__':
    app.run(debug=True)
