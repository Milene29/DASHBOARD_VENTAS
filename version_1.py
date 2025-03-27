import streamlit as st
import pandas as pd
import datetime
from difflib import get_close_matches
import funciones_generales as fg
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime, timedelta
import time
import streamlit as st
import time
import subprocess

st.set_page_config(layout="wide")

st.write(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# Parámetro de intervalo de refresco en segundos

def load_data():
    # Cargar datos de pagos reales

    # ID del archivo de Drive y hoja que quieres leer
    file_id = '1uML9hmrdOZVQ3Fa1GLDo7XkoWRbZSPgAcKYV1aFd6xs'  # ID del archivo específico
    # Descargar y leer la hoja específica del archivo Excel
    df = fg.descargar_archivo_drive(file_id)
    return df

@st.cache_data
def load_data2():
    # Cargar datos de pagos reales
    df_metas = pd.read_excel("Pagos_Meta.xlsx", sheet_name="Meta")
    
    return df_metas
# Load data
df = load_data()
# Load data
df_metas = load_data2()

# Botón manual para refrescar
boton = st.button("Actualizar data")
refresh_interval = 900
if boton :
    st.rerun()

# Define logic to classify careers into worlds
def clasificar_mundo(ult_programa_interes):
    if ult_programa_interes in [
        "COMUNICACIÓN", "COMUNICACIÓN AUDIOVISUAL Y CINE", "COMUNICACIÓN Y PUBLICIDAD TRANSMEDIA"
    ]:
        return "MUNDO COMUNICACIONES"
    elif ult_programa_interes in ["ARQUITECTURA", "ARQUITECTURA DE INTERIORES"]:
        return "MUNDO ARQUITECTURA"
    elif ult_programa_interes == "DISEÑO GRÁFICO PUBLICITARIO":
        return "MUNDO DISEÑO"
    elif ult_programa_interes in [
        "ADMINISTRACION", "ADMINISTRACIÓN Y MARKETING", "MARKETING E INNOVACIÓN",
        "ADMINISTRACIÓN Y NEGOCIOS INTERNACIONALES"
    ]:
        return "MUNDO NEGOCIOS"
    elif ult_programa_interes == "PSICOLOGÍA":
        return "MUNDO PSICOLOGIA"
    elif ult_programa_interes in ["DISEÑO ESTRATÉGICO", "INGENIERIA INDUSTRIAL"]:
        return "PORTAFOLIO ANTIGUO"
    elif pd.isna(ult_programa_interes):
        return "SIN CARRERA"


# Add a calculated column for Mundo
# Asignar 'SIN CARRERA' a las celdas vacías o nulas

carr_mapping = {
    "Comunicación Audiovisual y Cine": "COMUNICACIÓN AUDIOVISUAL Y CINE",
    "Arquitectura": "ARQUITECTURA",
    "Arquitectura de Interiores": "ARQUITECTURA DE INTERIORES",
    "Administración y Negocios Internacionales": "ADMINISTRACIÓN Y NEGOCIOS INTERNACIONALES",
    "Psicología": "PSICOLOGÍA",
    "Diseño Gráfico Publicitario": "DISEÑO GRÁFICO PUBLICITARIO",
    "Comunicación y Publicidad Transmedia": "COMUNICACIÓN Y PUBLICIDAD TRANSMEDIA",
    "Administración y Marketing": "ADMINISTRACIÓN Y MARKETING",
    "Administración": "ADMINISTRACIÓN",
    "Comunicación": "COMUNICACIÓN",
    "Marketing e Innovación": "MARKETING E INNOVACIÓN"
}
df['Carrera'] = df['Carrera'].replace(carr_mapping)
df['Carrera'] = df['Carrera'].fillna('SIN CARRERA')
df['MUNDO_CALCULADO'] = df['Carrera'].apply(clasificar_mundo)

df['Convalidación'] = df['Convalidación'].replace({0: 'No Convo', 1: 'Convo'})
df['Horario de Estudio'] = df['Horario de Estudio'].replace({'Nocturno - A distancia': 'RE', 'Diurno': 'PR','Nocturno - Psicologia':'RE'})


with st.sidebar:
    st.header("Filtros")
    
    # Filtro de mundos
    mundos_disponibles = ["TODAS LAS CARRERAS"] + df['MUNDO_CALCULADO'].dropna().unique().tolist()
    mundo_seleccionado = st.selectbox("Selecciona un mundo", options=mundos_disponibles)
    
    # Filtro de carreras dinámico según el mundo seleccionado
    if mundo_seleccionado == "TODAS LAS CARRERAS":
        carreras_disponibles = df['Carrera'].dropna().unique()
    
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["Todas"] + list(carreras_disponibles))

    elif mundo_seleccionado != "SIN CARRERA":
        carreras_disponibles = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]['ult_programa_interes'].dropna().unique()
       
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["Todas"] + list(carreras_disponibles))

    else:
        carrera_seleccionada = None


filtered_df = df.copy()

# Filtrar por mundo
if mundo_seleccionado != "TODAS LAS CARRERAS":
    filtered_df = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]

# Filtrar por mundo
if carrera_seleccionada != "Todas":
    filtered_df = df[(df['MUNDO_CALCULADO'] == mundo_seleccionado) & (df['Carrera'] == carrera_seleccionada) ]

# Filtrar por carrera
if mundo_seleccionado == "SIN CARRERA":

    filtered_df = df[
        (df['MUNDO_CALCULADO'] == "SIN CARRERA") 
    ]


# Mostrar resultados filtrados




with st.sidebar:

    
    tipo_ingreso =["Todos"] + filtered_df['Tipo de Ingreso'].unique().tolist()
    tipo_select= st.selectbox("Tipo Ingreso", options=tipo_ingreso)
    if tipo_select != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['Tipo de Ingreso'] == tipo_select]
     # Filtrar los IDs con Tipo de Ingreso = 1
   
 

    modalidad =["Todos"] + filtered_df['Horario de Estudio'].unique().tolist()
    moda_selec= st.selectbox("Modalidad", options=modalidad)
    if moda_selec != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['Horario de Estudio'] == moda_selec]

    canales_disponibles =["Todos"] + filtered_df['CANAL'].unique().tolist()
    canal_seleccionado= st.selectbox("Canal", options=canales_disponibles)
    if canal_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['CANAL'] == canal_seleccionado]

    subcanales_disponibles =["Todos"] + filtered_df['SUBCANAL'].unique().tolist()
    subcanal_seleccionado= st.selectbox("Subcanal", options=subcanales_disponibles)
    if subcanal_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['SUBCANAL'] == subcanal_seleccionado]
     
     

    Convo =["Todos"] + filtered_df['Convalidación'].unique().tolist()
    Convo_seleccionado= st.selectbox("Convo", options=Convo)
    if Convo_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['Convalidación'] == Convo_seleccionado]

##------------------------------------------------filtro fecha --------------------------------------------
min_fecha = filtered_df['Fecha de Pago'].min()
max_fecha = filtered_df['Fecha de Pago'].max()
col1,col2=st.columns([0.5,2])
with col1:
    rango_fechas = st.date_input(
                    "Selecciona el rango de fechas",
                    value=(pd.to_datetime(min_fecha).date(), pd.to_datetime(max_fecha).date()),  # Convertir str a datetime.date
                    help="Selecciona las fechas para filtrar los datos de ventas por carrera ."
                )

        
    rango_fechas_str = (
                rango_fechas[0].strftime("%Y-%m-%d"),
                rango_fechas[1].strftime("%Y-%m-%d")
            )

    filtered_df = filtered_df[
                (filtered_df['Fecha de Pago'] >= rango_fechas_str[0]) &
                (filtered_df['Fecha de Pago'] <= rango_fechas_str[1])
        ]
with col2:
    st.write("")
## ----------------------------------------------------------------------------------------------------


# FILTRAR LOS DATOS
filtered_df_2 = filtered_df[filtered_df['Convalidación'] == "No Convo"]


# CREAR LAS COLUMNAS DE VENTAS REGULAR Y VENTAS DISTANCIA
filtered_df_2['Ventas Regular'] = (filtered_df_2['Horario de Estudio'] != 'RE').astype(int)  # Todo lo que NO es RE es Regular
filtered_df_2['Ventas Distancia'] = (filtered_df_2['Horario de Estudio'] == 'RE').astype(int)  # Lo que es RE es Distancia

tabla_metricas = filtered_df_2.groupby('Carrera').agg(
    Semi_Presencial=('Ventas Regular', 'sum'),
    Distancia=('Ventas Distancia', 'sum')
).reset_index()
# Agregar columna de Total por fila
tabla_metricas['Total'] = tabla_metricas['Semi_Presencial'] + tabla_metricas['Distancia']

# Calcular el total y agregarlo como una fila adicional
# Calcular el total general y agregarlo como una fila adicional
total_regular = tabla_metricas['Semi_Presencial'].sum()
total_distancia = tabla_metricas['Distancia'].sum()
total_total = tabla_metricas['Total'].sum()
total_row = pd.DataFrame({'Carrera': ['TOTAL'], 'Semi_Presencial': [total_regular], 'Distancia': [total_distancia], 'Total': [total_total]})

# Concatenar el total a la tabla
tabla_metricas = pd.concat([tabla_metricas, total_row], ignore_index=True)

# Configurar tabla con AgGrid
gb = GridOptionsBuilder.from_dataframe(tabla_metricas)
gb.configure_side_bar()
gb.configure_column("Carrera", header_name="CARRERA 🎓", cellStyle={'color': 'black'})
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True)
grid_options = gb.build()

col1,col2,col3,col4=st.columns([1.8,0.1,0.7,0.6])
# Mostrar tabla en Streamlit

with col1:
    st.write("📊 **Matriz de Ventas por Carrera**")
    AgGrid(tabla_metricas, gridOptions=grid_options, fit_columns_on_grid_load=False, height=413, theme="blue", width='90%')
    
    
with col2:
    st.write("")
with col3:
    # Seleccionar la semana en curso
    hoy = datetime.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday()+1)  # Lunes de esta semana
    fin_semana = inicio_semana + timedelta(days=7)  # Domingo de esta semana
    print(".-----------------------------------------")
    inicio_semana2 = hoy - timedelta(days=hoy.weekday()) 
    # Formatear fechas
    inicio_semana_str = inicio_semana2.strftime("%d %B")
    fin_semana_str = fin_semana.strftime("%d %B")
    titulo_semana = f"Ventas Semana {inicio_semana_str} - {fin_semana_str}"

    # Filtrar pagos reales de la semana en curso
    df["Fecha de Pago"] = pd.to_datetime(df["Fecha de Pago"])
    df_semana = df[(df["Fecha de Pago"] >= inicio_semana) & (df["Fecha de Pago"] <= fin_semana)]
    print(df_semana["Fecha de Pago"])
    # Obtener metas de pagos de la semana en curso
    df_metas["Fecha"] = pd.to_datetime(df_metas["Fecha"])
    df_metas_semana = df_metas[(df_metas["Fecha"] >= inicio_semana) & (df_metas["Fecha"] <= fin_semana)]
    print(df_metas_semana["Fecha"])
    # Crear tabla resumen
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    resumen = {"Día": dias_semana, "Real": [], "Meta": []}

    for i in range(7):
        dia = inicio_semana + timedelta(days=i+1)
        pagos_reales = df_semana[df_semana["Fecha de Pago"].dt.date == dia.date()].shape[0]
        meta_pagos = df_metas_semana[df_metas_semana["Fecha"].dt.date == dia.date()]["Meta"].sum()
        
        resumen["Real"].append(pagos_reales)
        resumen["Meta"].append(meta_pagos if not pd.isna(meta_pagos) else 0)
    # Agregar fila "Total"
    resumen["Día"].append("Total")
    resumen["Real"].append(sum(resumen["Real"]))
    resumen["Meta"].append(sum(resumen["Meta"]))

    # Convertir a DataFrame
    tabla_pagos = pd.DataFrame(resumen)
    
    # Crear función para aplicar color según condiciones
    def color_real(val, meta):
        if val > meta:  # Verde si es mayor a la meta
            return 'background-color: #b9e8ac; color: black;font-weight: bold;'
        elif val == meta or val == meta - 1:  # Naranja si es igual o -1 de la meta
            return 'background-color: #f7d394; color: black;font-weight: bold;'
        elif val <= meta - 2:  # Rojo si es -2 o menor que la meta
            return 'background-color: #f5877a; color: black; font-weight: bold;'
        return ''
    # Aplicar colores a la columna "Real"
    tabla_pagos_style = tabla_pagos.style.apply(
        lambda row: [color_real(row['Real'], row['Meta']) if col == "Real" else "" for col in row.index], axis=1
    ).format({"Real": "{:,.0f}", "Meta": "{:,.0f}"})  # Formatear números sin decimales

    # Mostrar en Streamlit
    st.write(f"📊 **{titulo_semana}**")
    st.dataframe(tabla_pagos_style, hide_index=True)
# Función para filtrar el DataFrame y contar "Evaluando" e "Interesado"




def cargar_datos_excel():
        # Paso 1: Ejecutar el script `CORTE_2.PY`
    ruta_script = "CORTE_2.PY"
    subprocess.run(["python", ruta_script])  # Ejecuta el script y espera a que termine

    # Paso 2: Leer el archivo Excel generado
    ruta_excel = "reporte_prometeo/corte_del_dia.xls"
    df_corte = pd.read_excel(ruta_excel)
            
    return df_corte

   
if boton:
    st.cache_data.clear()
    df_corte = cargar_datos_excel()
else:
    df_corte = cargar_datos_excel()
    

nombre_mapping = {
    "Rosa Natalia Ugarte Chavez": "Rosa Ugarte",
    "Sergio Valderrama Rodriguez": "Sergio Valderrama",
    "Daniel Enrique Zapata Alvarado": "Daniel Zapata",
    "INGRID GUILLERMO RIVERA": "Ingrid Guillermo",
    "Fabiola Galindo": "Fabiola Galindo",
    "Rosmery Enriquez": "Rosmery Enriquez",
    "Andrea Alejandra Crisanto Navarro":"Andrea Crisanto",
    "ERWIN TERIE VITAL AVILA":"Erwyn Terie",
    "Andrea Araujo Antara":"Andrea Araujo"
}


df_corte['vendedor'] = df_corte['vendedor'].replace(nombre_mapping)


col1,col2=st.columns([3.1,2.5])   
with col1:
    st.write("")
with col2:
        def crear_tabla_asesores(df_corte, df_ventas):
            # Filtrar datos excluyendo "TI Integrador"
            df_corte = df_corte[df_corte["vendedor"] != "TI Integrador"]

            # Crear un DataFrame vacío para la tabla final
            tabla_final = pd.DataFrame(columns=["Asesor",  "Interesado", "Evaluando","Visitas", "PP","Cargos", "Ventas"])
            
            # Obtener lista única de asesores en df_corte (sin "TI Integrador")
            asesores = df_corte["vendedor"].unique()
            df_ventas["Asesor Homologado"] = df_ventas["Asesor Homologado"].fillna("").astype(str)

            # Recorrer cada asesor y calcular Evaluando, Interesado
            for asesor in asesores:
                evaluando_count = df_corte[(df_corte["vendedor"] == asesor) & (df_corte["respuesta"] == "Evaluando")].shape[0]
                interesado_count = df_corte[(df_corte["vendedor"] == asesor) & (df_corte["respuesta"] == "Interesado")].shape[0]

                # Buscar el nombre más cercano del asesor en la base df_ventas usando get_close_matches
                nombre_ventas = get_close_matches(asesor, df_ventas["Asesor Homologado"].unique(), n=1, cutoff=0.6)
                nombre_ventas = nombre_ventas[0] if nombre_ventas else asesor  # Usar nombre encontrado o el original si no hay match

                # Obtener la cantidad de ventas de ese asesor desde df_ventas (filtrando ventas del día actual)
                ventas_count = df_ventas[(df_ventas["Asesor Homologado"] == nombre_ventas) & (df_ventas["Fecha de Pago"] == pd.Timestamp.today().normalize())].shape[0]

                # Agregar los datos del asesor a la tabla final (Visitas y Cargos quedarán vacías para completar luego)
                tabla_final = pd.concat([tabla_final, pd.DataFrame([[asesor,  interesado_count,evaluando_count, 0, 0, 0,ventas_count]],
                                                                columns=tabla_final.columns)], ignore_index=True)
            
            return tabla_final
        # Crear la tabla final

        tabla_final = crear_tabla_asesores(df_corte, df)
        # Mostrar la tabla en Streamlit
        st.write("📊 **Gestión de Ventas por Asesor**")
        editable_tabla_final = st.data_editor(
            tabla_final,
            key="tabla_final",
            hide_index=True,
            disabled=["Asesor", "Evaluando", "Interesado", "Ventas"],
        )
                
        # Sumar totales de columnas específicas desde la tabla editable
        total_visitas = editable_tabla_final["Visitas"].sum()
        total_cargos = editable_tabla_final["Cargos"].sum()
        total_evaluando = editable_tabla_final["Evaluando"].sum()
        total_interesado = editable_tabla_final["Interesado"].sum()
        total_ventas = editable_tabla_final["Ventas"].sum()
        total_pp = editable_tabla_final["PP"].sum()

hoy_str = hoy.strftime("%d %B")  # Fecha en formato 'día mes'

    # Crear DataFrame con las filas predefinidas y valores iniciales en 0
data = {
    "Métrica": [ "Evaluando", "Interesado","Visitas","PP", "Cargos", "Ventas"],
    "Cantidad": [  total_evaluando,total_interesado,total_visitas, total_pp,  total_cargos,total_ventas],
}
df_resumen = pd.DataFrame(data)
    


      
    
print("............................................")   
with col4:
    st.write(f"📊 **Resumen del día - {hoy_str}**")
    st.dataframe(df_resumen, hide_index=True)
    print("salio 22")
    
    
time.sleep(refresh_interval)
# Configurar auto-refresh con st.rerun basado en el intervalo seleccionado
st.rerun()  
