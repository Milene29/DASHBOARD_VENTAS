import streamlit as st
import pandas as pd
import datetime
from difflib import get_close_matches
import funciones_generales as fg
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime, timedelta

import subprocess

# Set page config
st.set_page_config(page_title="Streamlit Dashboard", layout="wide")



# Define function to get today's date in Lima timezone

@st.cache_data
def load_data():
    # Cargar datos de pagos reales

    # ID del archivo de Drive y hoja que quieres leer
    file_id = '1uML9hmrdOZVQ3Fa1GLDo7XkoWRbZSPgAcKYV1aFd6xs'  # ID del archivo específico
    # Descargar y leer la hoja específica del archivo Excel
    df = fg.descargar_archivo_drive(file_id)
    df_metas = pd.read_excel("Pagos_Meta.xlsx", sheet_name="Meta")
    
    return df,df_metas
# Load data

if st.button("Actualizar data"):
    st.cache_data.clear()  # Limpiar la caché
    df,df_metas = load_data()
    print("Boton 1")
else:
    df,df_metas = load_data()
# Mostrar algunos datos para verificar que funcionó

st.markdown(
    """   
    <h1 style="
        background: linear-gradient(90deg, #1E90FF, #8A2BE2, #4169E1); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-size: 50px; 
        text-align: center; 
        font-weight: bold; 
        margin-bottom: 20px;">
        VENTAS UCAL 25.1
    </h1>
    """,
    unsafe_allow_html=True
)

# Helper function to format numbers with commas
def format_with_commas(number):
    return f"{number:,}"

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


rango_fechas = st.date_input(
                "Selecciona el rango de fechas",
                value=(pd.to_datetime(min_fecha).date(), pd.to_datetime(max_fecha).date()),  # Convertir str a datetime.date
                help="Selecciona las fechas para filtrar los datos de conversión ."
            )

    
rango_fechas_str = (
            rango_fechas[0].strftime("%Y-%m-%d"),
            rango_fechas[1].strftime("%Y-%m-%d")
        )

filtered_df = filtered_df[
            (filtered_df['Fecha de Pago'] >= rango_fechas_str[0]) &
            (filtered_df['Fecha de Pago'] <= rango_fechas_str[1])
        ]
## ----------------------------------------------------------------------------------------------------


# FILTRAR LOS DATOS
filtered_df_2 = filtered_df[filtered_df['Convalidación'] == "No Convo"]


# CREAR LAS COLUMNAS DE VENTAS REGULAR Y VENTAS DISTANCIA
filtered_df_2['Ventas Regular'] = (filtered_df_2['Horario de Estudio'] != 'RE').astype(int)  # Todo lo que NO es RE es Regular
filtered_df_2['Ventas Distancia'] = (filtered_df_2['Horario de Estudio'] == 'RE').astype(int)  # Lo que es RE es Distancia

tabla_metricas = filtered_df_2.groupby('Carrera').agg(
    Regular=('Ventas Regular', 'sum'),
    Distancia=('Ventas Distancia', 'sum')
).reset_index()

# Calcular el total y agregarlo como una fila adicional
total_regular = tabla_metricas['Regular'].sum()
total_distancia = tabla_metricas['Distancia'].sum()
total_row = pd.DataFrame({'Carrera': ['TOTAL'], 'Regular': [total_regular], 'Distancia': [total_distancia]})

# Concatenar el total a la tabla
tabla_metricas = pd.concat([tabla_metricas, total_row], ignore_index=True)

# Configurar tabla con AgGrid
gb = GridOptionsBuilder.from_dataframe(tabla_metricas)
gb.configure_side_bar()
gb.configure_column("Carrera", header_name="CARRERA 🎓", cellStyle={'fontWeight': 'bold'})
gb.configure_default_column(groupable=False, value=True, enableRowGroup=True, editable=True)
grid_options = gb.build()

col1,col2,col3,col4=st.columns([1.8,0.1,1,1])
# Mostrar tabla en Streamlit

with col1:
    st.write("📊 **MATRIZ DE VENTAS POR CARRERA**")
    AgGrid(tabla_metricas, gridOptions=grid_options, fit_columns_on_grid_load=False, height=320, theme="blue", width='80%')
    
    
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
    # Mostrar en Streamlit
    st.write(f"📊 **{titulo_semana}**")
    st.dataframe(tabla_pagos.style.format({"Real": "{:,.0f}", "Meta": "{:,.0f}"}), hide_index=True)
# Función para filtrar el DataFrame y contar "Evaluando" e "Interesado"





# Paso 1: Función para calcular las métricas
def calcular_métricas(df_corte):
    # Filtrar registros excluyendo el vendedor "TI Integrador"
    df_corte = df_corte[df_corte["vendedor"] != "TI Integrador"]

    # Filtrar y contar las filas de "Evaluando" y "Interesado"
    evaluando_count = df_corte[df_corte["respuesta"] == "Evaluando"].shape[0]
    interesado_count = df_corte[df_corte["respuesta"] == "Interesado"].shape[0]

    return evaluando_count, interesado_count

@st.cache_data
def cargar_datos_excel():
        # Paso 1: Ejecutar el script `CORTE_2.PY`
    ruta_script = "CORTE_2.PY"
    subprocess.run(["python", ruta_script])  # Ejecuta el script y espera a que termine

    # Paso 2: Leer el archivo Excel generado
    ruta_excel = "reporte_prometeo\corte_del_dia.xls"
    df_corte = pd.read_excel(ruta_excel)
    
    
    
    return df_corte

df_corte = cargar_datos_excel()
evaluando_count, interesado_count = calcular_métricas(df_corte)

hoy_str = hoy.strftime("%d %B")  # Fecha en formato 'día mes'

# Filtrar pagos reales del día de hoy
df["Fecha de Pago"] = pd.to_datetime(df["Fecha de Pago"])  # Asegurar formato datetime
pagos_hoy = df[df["Fecha de Pago"].dt.date == hoy.date()].shape[0]  # Cantidad de pagos del día actual


    # Crear DataFrame con las filas predefinidas y valores iniciales en 0
data = {
    "Métrica": ["Ventas", "PP", "Cargos", "Evaluando", "Interesado", "Visitas"],
    "Cantidad": [pagos_hoy, 0, 0, evaluando_count, interesado_count, 0],
}
df_resumen = pd.DataFrame(data)
        
print("............................................")   
with col4:
    st.write(f"📊 **Tabla Resumen - Fecha: {hoy_str}**")
    if not st.button("Refrescar tabla"):
        
            # Permitir que el usuario edite la tabla (excepto el campo 'Ventas')
        editable_df = st.data_editor(
            df_resumen,
            disabled=["Ventas","Evaluando","Interesado"],  # Deshabilitar edición de la fila 'Ventas'
            key="tabla_resumen",
            hide_index=True,
            )
        print("salio 22")
    else:
        print("entro")
        # Ejecutar script externo

        ruta_script = "CORTE_2.PY"
        subprocess.run(["python", ruta_script])  # Ejecuta el script y espera a que termine

     # Paso 2: Leer el archivo Excel generado
        ruta_excel = r"reporte_prometeo\corte_del_dia.xls"
        df_corte = pd.read_excel(ruta_excel)
        evaluando_count, interesado_count = calcular_métricas(df_corte)

        # Actualizar la tabla con nuevos valores
        data = {
            "Métrica": ["Ventas", "PP", "Cargos", "Evaluando", "Interesado", "Visitas"],
            "Cantidad": [0, 0, 0, evaluando_count, interesado_count, 0],
        }
        df_resumen = pd.DataFrame(data)

        # Actualizar la tabla editable con los datos recalculados
        editable_df = st.data_editor(
            df_resumen,
            disabled=["Ventas", "Evaluando", "Interesado"],
            key="tabla_resumen",
            hide_index=True,
            
        )
        print("salio")
    
        
        
        
        
print("............................................")   
print(df["Asesor Homologado"])    
def crear_tabla_asesores(df_corte, df_ventas):
    # Filtrar datos excluyendo "TI Integrador"
    df_corte = df_corte[df_corte["vendedor"] != "TI Integrador"]

    # Crear un DataFrame vacío para la tabla final
    tabla_final = pd.DataFrame(columns=["Asesor", "Evaluando", "Interesado", "Visitas", "Cargos", "Ventas"])
    
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
        tabla_final = pd.concat([tabla_final, pd.DataFrame([[asesor, evaluando_count, interesado_count, 0, 0, ventas_count]],
                                                          columns=tabla_final.columns)], ignore_index=True)
    
    return tabla_final
# Crear la tabla final
print(df.columns)
tabla_final = crear_tabla_asesores(df_corte, df)
# Mostrar la tabla en Streamlit
st.write("📊 **GESTIÓN DE VENTAS X ASESOR**")
st.dataframe(tabla_final,hide_index=True) 