from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


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

def generar_graficos():
    con = sqlite3.connect('datos.db')

    df_incidentes = pd.read_sql_query('SELECT * FROM Incidentes', con)
    df_contactos = pd.read_sql_query('SELECT * FROM Contactos', con)

    # Convertir fechas a formato datetime
    df_incidentes['fecha_apertura'] = pd.to_datetime(df_incidentes['fecha_apertura'], errors='coerce')
    df_incidentes['fecha_cierre'] = pd.to_datetime(df_incidentes['fecha_cierre'], errors='coerce')

    # Calcular tiempo de resolución
    df_incidentes['tiempo_resolucion'] = (df_incidentes['fecha_cierre'] - df_incidentes['fecha_apertura']).dt.days

    # Mostrar la media de tiempo (apertura-cierre) de los incidentes agrupando entre los que son de mantenimiento y los que no.
    media_tiempo_mantenimiento = df_incidentes[df_incidentes['es_mantenimiento'] == True]['tiempo_resolucion'].mean()
    media_tiempo_no_mantenimiento = df_incidentes[df_incidentes['es_mantenimiento'] == False]['tiempo_resolucion'].mean()

    plt.figure(figsize=(10, 5))
    plt.bar(['Mantenimiento', 'No Mantenimiento'], [media_tiempo_mantenimiento, media_tiempo_no_mantenimiento])
    plt.xlabel('Tipo de Incidencia')
    plt.ylabel('Media de Tiempo (días)')
    plt.title('Media de Tiempo de Resolución por Tipo de Incidencia')
    plt.savefig('static/media_tiempo_resolucion.png')

    # Mostrar por tipo de incidente una gráfica de “bigotes” (boxplot) con los tiempos de resolución representando los percentiles 5% y 90%.
    plt.figure(figsize=(10, 5))
    df_boxplot_data = df_incidentes[['tipo_incidencia', 'tiempo_resolucion']].copy()

    # Ordenar los tipos de incidencia
    df_boxplot_data['tipo_incidencia'] = df_boxplot_data['tipo_incidencia'].astype(int)
    df_boxplot_data = df_boxplot_data.sort_values('tipo_incidencia')

    boxplot_data_grouped_by_tipo_incidencia = [df_boxplot_data[df_boxplot_data['tipo_incidencia'] == tipo]['tiempo_resolucion'] for tipo in sorted(df_boxplot_data['tipo_incidencia'].unique())]

    plt.boxplot(boxplot_data_grouped_by_tipo_incidencia, labels=sorted(df_boxplot_data['tipo_incidencia'].unique()), showfliers=False)
    plt.xlabel('Tipo de Incidencia')
    plt.ylabel('Tiempo de Resolución (días)')
    plt.title('Boxplot de Tiempos de Resolución por Tipo de Incidencia')
    plt.savefig('static/boxplot_tiempos_resolucion.png')

    # Mostrar los 5 clientes más críticos
    df_criticos = df_incidentes[
        (df_incidentes['es_mantenimiento'] == True) &
        (df_incidentes['tipo_incidencia'] != 1)
    ]
    top_5_clientes = df_criticos['cliente'].value_counts().head(5)

    plt.figure(figsize=(10, 5))
    top_5_clientes.plot(kind='bar', color='skyblue')
    plt.xlabel('Cliente')
    plt.ylabel('Número de Incidentes')
    plt.title('Top 5 Clientes Más Críticos')
    plt.savefig('static/top_5_clientes_criticos.png')

    # Mostrar número total de actuaciones por empleados
    actuaciones_por_empleado = df_contactos.groupby('id_emp').size()

    plt.figure(figsize=(10, 5))
    actuaciones_por_empleado.plot(kind='bar', color='orange')
    plt.xlabel('Empleado')
    plt.ylabel('Número de Actuaciones')
    plt.title('Total de Actuaciones por Empleados')
    plt.savefig('static/actuaciones_por_empleados.png')

    # Mostrar actuaciones totales según el día de la semana
    df_incidentes['dia_semana'] = df_incidentes['fecha_apertura'].dt.day_name()
    actuaciones_por_dia = df_contactos.merge(
        df_incidentes[['id', 'dia_semana']], left_on='incidente_id', right_on='id'
    )['dia_semana'].value_counts()

    plt.figure(figsize=(10, 8))
    actuaciones_por_dia.plot(kind='bar', color='green')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Total de Actuaciones')
    plt.title('Actuaciones por Día de la Semana')
    plt.savefig('static/actuaciones_por_dia.png')


    con.close()


@app.route('/')
def index():
    resultados, resultados_fraude = obtener_datos()
    generar_graficos()
    return render_template('index.html', resultados=resultados, resultados_fraude=resultados_fraude)
if __name__ == '__main__':
    app.run(debug=True)
