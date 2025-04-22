import streamlit as st
import pandas as pd
import datetime
from difflib import get_close_matches
import funciones_generales as fg
from datetime import datetime, timedelta
import time
import streamlit as st
import time
import subprocess
import os

st.set_page_config(page_title="Streamlit", layout="wide")

st.write(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# Parámetro de intervalo de refresco en segundos

st.write(
    """
    <style>
    .colored-title {
        color: #1E90FF;  /* Cambia el color */
        font-size: 30px;  /* Ajusta el tamaño */
        font-weight: bold;
        text-align: center;
    }
    </style>
    <div class="colored-title">Ventas UCAL 25.2</div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    # Cargar datos de pagos reales

    # ID del archivo de Drive y hoja que quieres leer
    file_id = '1uML9hmrdOZVQ3Fa1GLDo7XkoWRbZSPgAcKYV1aFd6xs'  # ID del archivo específico

    # Descargar y leer la hoja específica del archivo Excel
    df = fg.descargar_archivo_drive(file_id)

    return df
def load_data3():
    # Cargar datos de pagos reales

    # ID del archivo de Drive y hoja que quieres leer
 # ID del archivo específico
    file_id_2='1wLewUXO5ISe2qCDJnTXUf4WdGCA1z8DgP-GO55cUJVI'
    # Descargar y leer la hoja específica del archivo Excel

    df_252=fg.descargar_archivo_drive(file_id_2)
    return df_252

@st.cache_data
def load_data2():
    # Cargar datos de pagos reales
    df_metas = pd.read_excel("Pagos_Meta.xlsx", sheet_name="Meta")
    return df_metas
# Load data
df = load_data()
df_252=load_data3()
# Load data
df_metas = load_data2()

# Botón manual para refrescar
boton = st.button("Actualizar data")
col1,col2,col3=st.columns([1,1,2])
with col2:
    agrupacion_seleccionada = st.selectbox("Campaña: ", ["25.2", "25.1"])
    df = df_252 if agrupacion_seleccionada == "25.2" else df
    df['Carrera'] = df_252['CARRERA'] if agrupacion_seleccionada == "25.2" else df['Carrera']
    df['Convalidación'] = df_252['FLAG ACEPTO CONVA'] if agrupacion_seleccionada == "25.2" else df['Convalidación']
    df['Horario de Estudio'] = df_252['HORARIO DE ESTUDIO'] if agrupacion_seleccionada == "25.2" else df['Horario de Estudio']
    df['Tipo de Ingreso'] = df_252['TIPO DE INGRESO'] if agrupacion_seleccionada == "25.2" else df['Tipo de Ingreso']
    df['Fecha de Pago'] = df_252['FECHA DE PAGO'] if agrupacion_seleccionada == "25.2" else df['Fecha de Pago']
    df['Asesor Homologado'] = df_252['ASESOR HOMOLOGADO'] if agrupacion_seleccionada == "25.2" else df['Asesor Homologado']

with col3:
    st.write("")    
if boton :
    st.rerun()
# Forzar recarga automática

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
#df['Carrera'] = df['Carrera'].replace(carr_mapping)
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
    
      
    elif mundo_seleccionado != "SIN CARRERA":
        carreras_disponibles = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]['Carrera'].dropna().unique()

    else:
        carrera_seleccionada = None
filtered_df = df.copy()

# Filtrar por mundo
if mundo_seleccionado != "TODAS LAS CARRERAS":
    filtered_df = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]

# Filtrar por carrera
if mundo_seleccionado == "SIN CARRERA":

    filtered_df = df[
        (df['MUNDO_CALCULADO'] == "SIN CARRERA") 
    ]


with st.sidebar:

    
    tipo_ingreso =["Todos"] + filtered_df['Tipo de Ingreso'].unique().tolist()
    tipo_select= st.selectbox("Tipo Ingreso", options=tipo_ingreso)
    if tipo_select != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['Tipo de Ingreso'] == tipo_select]
     
     # Filtrar los IDs con Tipo de Ingreso = 1
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


##------------------------------------------------filtro fecha --------------------------------------------
min_fecha = filtered_df['Fecha de Pago'].min()
max_fecha = filtered_df['Fecha de Pago'].max()

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

## ----------------------------------------------------------------------------------------------------

print("++++++++++++++++++++++")
print(filtered_df['Tipo de Ingreso'])
# CREAR LAS COLUMNAS DE VENTAS REGULAR Y VENTAS DISTANCIA
if tipo_select=='TRASLADO':
    # hacer algo
    filtered_df_3=(filtered_df[filtered_df['Tipo de Ingreso'] == 'TRASLADO'])
    filtered_df_3['Traslados Conva'] = (filtered_df_3['Convalidación'] != 'No Convo').astype(int)  # Todo lo que NO es RE es Regular
    filtered_df_3['Traslados sin Conva'] = (filtered_df_3['Convalidación'] == 'No Convo').astype(int)  # Lo que es RE es Distancia
        
    tabla_metricas = filtered_df_3.groupby('Carrera').agg(
        Conva=('Traslados Conva', 'sum'),
        Sin_conva=('Traslados sin Conva', 'sum')
    ).reset_index()
    # Agregar columna de Total por fila
    tabla_metricas['Total'] = tabla_metricas['Conva'] + tabla_metricas['Sin_conva']
    
    total_conva = tabla_metricas['Conva'].sum()
    total_sinconva = tabla_metricas['Sin_conva'].sum()
    total_total = tabla_metricas['Total'].sum()
    total_row = pd.DataFrame({'Carrera': ['TOTAL'], 'Conva': [total_conva], 'Sin_conva': [total_sinconva], 'Total': [total_total]})

    # Concatenar el total a la tabla
    tabla_metricas = pd.concat([tabla_metricas, total_row], ignore_index=True)
    
    

    def style_dataframe2(df):
        return df.style.set_table_styles(
            [
                
                
                {'selector': 'thead th',  # Estilos solo para las cabeceras
                'props': [
                    ('background-color', '#001f54'),  # Azul oscuro
                    ('color', 'white'),               # Texto blanco
                    ('font-weight', 'bold'),          # Negrita en cabeceras
                    ('text-align', 'center'),
                    ('font-family', 'Arial, sans-serif'),
                    ('font-size', '14px'),
                    ('width', '80px')   
                ]},
                {'selector': 'thead th:nth-child(1)',  # La primera columna ("Carrera")
                'props': [('width', '390px'),  # Ancho mayor solo para "Carrera"
                        ('text-align', 'left'),
    ]  # Alineación a la izquierda opcional
                },  
                {'selector': 'td, th',  # Bordes en toda la tabla
                'props': [('border', '0.5px solid #001f54')]},  # Bordes azul oscuro
                {'selector': 'tr:nth-child(even) td',  # Filas pares
                'props': [('background-color', '#f4f4f4')]}  # Fondo gris claro alternado
            ]
        ).set_properties(
            subset=['Conva', 'Sin_conva', 'Total'],
            **{'text-align': 'center'}).apply(
            lambda row: ['font-weight: bold; background-color: #f8d7da; color: black;' if row.name == len(df) - 1 else '' for _ in row], 
            axis=1
        )

    styled_df_html = style_dataframe2(tabla_metricas).hide(axis='index').to_html()

    

else:
    filtered_df_2 =filtered_df
    filtered_df_2['Ventas Regular'] = (filtered_df_2['Horario de Estudio'] != 'RE').astype(int)  # Todo lo que NO es RE es Regular
    filtered_df_2['Ventas Distancia'] = (filtered_df_2['Horario de Estudio'] == 'RE').astype(int)  # Lo que es RE es Distancia

    tabla_metricas = filtered_df_2.groupby('Carrera').agg(
            Semi_Presencial=('Ventas Regular', 'sum'),
            Distancia=('Ventas Distancia', 'sum')
        ).reset_index()
        # Agregar columna de Total por fila
    tabla_metricas = tabla_metricas.rename(columns={
    'Semi_Presencial':'Semi Presencial'
})
    tabla_metricas['Total'] = tabla_metricas['Semi Presencial'] + tabla_metricas['Distancia']

        # Calcular el total y agregarlo como una fila adicional
        # Calcular el total general y agregarlo como una fila adicional
    total_regular = tabla_metricas['Semi Presencial'].sum()
    total_distancia = tabla_metricas['Distancia'].sum()
    total_total = tabla_metricas['Total'].sum()
    total_row = pd.DataFrame({'Carrera': ['TOTAL'], 'Semi Presencial': [total_regular], 'Distancia': [total_distancia], 'Total': [total_total]})

        # Concatenar el total a la tabla
    tabla_metricas = pd.concat([tabla_metricas, total_row], ignore_index=True)
    
        
    def style_dataframe3(df):
        return df.style.set_table_styles(
            [
                
                
                {'selector': 'thead th',  # Estilos solo para las cabeceras
                'props': [
                    ('background-color', '#001f54'),  # Azul oscuro
                    ('color', 'white'),               # Texto blanco
                    ('font-weight', 'bold'),          # Negrita en cabeceras
                    ('text-align', 'center'),
                    ('font-family', 'Arial, sans-serif'),
                    ('font-size', '13px'),
                    ('width', '100px')   
                ]},
                {'selector': 'thead th:nth-child(1)',  # La primera columna ("Carrera")
                'props': [('width', '350px'),  # Ancho mayor solo para "Carrera"
                        ('text-align', 'left'),
    ]  # Alineación a la izquierda opcional
                },  
                {'selector': 'td',
            'props': [('width', '100px'),    # Ancho reducido para las celdas en general
                      ('font-size', '15px')]},
                
                {'selector': 'td, th',  # Bordes en toda la tabla
                'props': [('border', '0.5px solid #001f54')]},  # Bordes azul oscuro
                {'selector': 'tr:nth-child(even) td',  # Filas pares
                'props': [('background-color', '#f4f4f4')]},  # Fondo gris claro alternado
            {'selector': 'table',  # Ancho máximo de la tabla
            'props': [('max-width', '100%')]},  # Fondo gris claro alternado
            ]
        ).set_properties(
            subset=['Semi Presencial', 'Distancia', 'Total'],
            **{'text-align': 'center'}).apply(
            lambda row: ['font-weight: bold; background-color: #f8d7da; color: black;' if row.name == len(df) - 1 else '' for _ in row], 
            axis=1
        )
    styled_df_html = style_dataframe3(tabla_metricas).hide(axis='index').to_html()


with st.container():
    col1principal,col2principal=st.columns([1,1])
    # Mostrar tabla en Streamlit
    with col1principal:
        col1,col2=st.columns([3,0.2])
        with col1:
            st.write("📊 **Matriz de Ventas por Carrera**")
            st.markdown(styled_df_html, unsafe_allow_html=True)
        with col2:
            st.write("")
            
    with col2principal:
        col2,col3=st.columns([1,1])

        with col2:
            # Seleccionar la semana en curso
            hoy = datetime.today()
            inicio_semana = hoy - timedelta(days=hoy.weekday()+1)  # Lunes de esta semana
            fin_semana = inicio_semana + timedelta(days=7)  # Domingo de esta semana
            inicio_semana2 = hoy - timedelta(days=hoy.weekday()) 
            # Formatear fechas
            inicio_semana_str = inicio_semana2.strftime("%d %B")
            fin_semana_str = fin_semana.strftime("%d %B")
            titulo_semana = f"Ventas Semana: {inicio_semana_str} - {fin_semana_str}"

            # Filtrar pagos reales de la semana en curso
            df["Fecha de Pago"] = pd.to_datetime(df["Fecha de Pago"])
            df_semana = df[(df["Fecha de Pago"] >= inicio_semana) & (df["Fecha de Pago"] <= fin_semana)]
            # Obtener metas de pagos de la semana en curso
            df_metas["Fecha"] = pd.to_datetime(df_metas["Fecha"])
            
            df_metas_semana = df_metas[(df_metas["Fecha"] >= inicio_semana) & (df_metas["Fecha"] <= fin_semana)]
            print(df_metas_semana)
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
            resumen["Día"].append("TOTAL")
            resumen["Real"].append(sum(resumen["Real"]))
            resumen["Meta"].append(sum(resumen["Meta"]))

            # Convertir a DataFrame
            tabla_pagos = pd.DataFrame(resumen)
            def style_dataframe_general(df):
                styles = []
                
                # Agregar estilos para la cabecera
                styles.append({
                    'selector': 'thead th',
                    'props': [
                        ('background-color', '#001f54'),  # Azul marino
                        ('color', 'white'),
                        ('font-family', 'Arial, sans-serif'),
                        ('font-size', '13px'),
                        ('text-align', 'center')
                    ]
                })

                # Agregar estilos dinámicos (colores según condiciones) para cada fila basada en 'Real'
                for i, row in df.iterrows():
                    if row['Real'] > row['Meta']:
                        styles.append({
                            'selector': f'tr:nth-child({i + 1}) td:nth-child(2)',  # "Real" es la 2ª columna
                            'props': [('background-color', '#b9e8ac'), ('color', 'black')]
                        })
                    elif row['Real'] == row['Meta'] or row['Real'] == row['Meta'] - 1:
                        styles.append({
                            'selector': f'tr:nth-child({i + 1}) td:nth-child(2)',  # Aplicado solo a la 2ª columna
                            'props': [('background-color', '#f7d394'), ('color', 'black')]
                        })
                    elif row['Real'] <= row['Meta'] - 2:
                        styles.append({
                            'selector': f'tr:nth-child({i + 1}) td:nth-child(2)',
                            'props': [('background-color', '#f5877a'), ('color', 'black')]
                        })

                    # Aplicar estilos generales (bordes)
                    styles.append({
                        'selector': 'td, th',
                       'props': [
        ('border', '0.5px solid #001f54'),
       ('height', '15px') # si deseas que todas tengan ese ancho
    ]
                    })
        
                # Aplicar estilos dinámicos a toda la tabla
                return df.style.set_table_styles(styles).set_properties(subset=['Real', 'Meta'],  # Centrando las columnas "Real" y "Meta"
                **{'text-align': 'center'}).apply(
                lambda row: ['font-weight: bold;background-color: white !important;color: black;' if row.name == len(df) - 1 else '' for _ in row], 
                axis=1)
            # Mostrar en Streamlit
            st.write(f"📊 **{titulo_semana}**")
            styled_df_html = style_dataframe_general(tabla_pagos).hide(axis='index').to_html()
            st.markdown(styled_df_html, unsafe_allow_html=True)
        # Función para filtrar el DataFrame y contar "Evaluando" e "Interesado"



        @st.cache_data
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
            st.session_state.tabla_final = None 
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



        
        FILE_PATH = "tabla_final.xlsx"
        columnas = ["Asesor", "Interesado", "Evaluando", "Visitas", "PP", "Cargos", "Ventas"]    
        editables = ["Visitas", "PP", "Cargos"]  # Columnas que el usuario puede modificar
        def cargar_datos():
            if os.path.exists(FILE_PATH):
                return pd.read_excel(FILE_PATH)
            else:
                return pd.DataFrame(columns=columnas).fillna(0)
        def crear_tabla_asesores(df_corte, df_ventas):
                    # Filtrar datos excluyendo "TI Integrador"
            df_corte = df_corte[df_corte["vendedor"] != "TI Integrador"]
            tabla_guardada = cargar_datos()
            tabla_final = pd.DataFrame(columns=columnas)
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
                if asesor in tabla_guardada["Asesor"].values:
                            visitas = tabla_guardada.loc[tabla_guardada["Asesor"] == asesor, "Visitas"].values[0]
                            pp = tabla_guardada.loc[tabla_guardada["Asesor"] == asesor, "PP"].values[0]
                            cargos = tabla_guardada.loc[tabla_guardada["Asesor"] == asesor, "Cargos"].values[0]
                else:
                    visitas, pp, cargos = 0, 0, 0  # Si no hay datos previos, inicializar en 0

                                        # Agregar los datos del asesor a la tabla final (Visitas y Cargos quedarán vacías para completar luego)
                tabla_final = pd.concat([tabla_final, pd.DataFrame([[asesor,  interesado_count,evaluando_count, visitas, pp, cargos,ventas_count]],
                                                                        columns=tabla_final.columns)], ignore_index=True)
                    
            return tabla_final
                # Crear la tabla final

        tabla_final = crear_tabla_asesores(df_corte, df)
                # Mostrar la tabla en Streamlit

        st.write("")
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
        def style_dataframe1(df):
            return df.style.set_table_styles(
                [   
                    {'selector': 'thead th',  # Estilos solo para las cabeceras
                    'props': [
                        ('background-color', '#001f54'),  # Azul marino
                        ('color', 'white'),  # Texto blanco
                        ('font-family', 'Arial, sans-serif'),
                        ('font-size', '14px'),
                        ('text-align', 'center')
                    ]
                    },
                    {'selector': 'tr:nth-child(even) td',  # Estilo para las filas pares
                    'props': [('background-color', '#f2f2f2')]},  # Color plomo claro
                    {'selector': 'td, th',  # Bordes en toda la tabla
                    'props': [('border', '0.5px solid #001f54')]}  # Bordes en azul marino
                ]
            ).set_properties(
                subset=['Cantidad'],  # Centrando columnas numéricas
                **{'text-align': 'center'}
            ) # Ocultar índice
        # Estilizar el DataFrame y mostrarlo en Streamlit como HTML
        styled_df_html3 = style_dataframe1(df_resumen).hide(axis='index').to_html()

        with col3:
            st.write(f"📊 **Resumen del día: {hoy_str}**")
            st.markdown(styled_df_html3, unsafe_allow_html=True)
                
            if "last_cache_clear" not in st.session_state:
                st.session_state.last_cache_clear = datetime.now()

            if datetime.now() - st.session_state.last_cache_clear >= timedelta(minutes=15):
                print('se borra el cache')
                cargar_datos_excel.clear()  # Borrar la caché
                st.session_state.last_cache_clear = datetime.now()  # Actualizar el tiempo de limpieza

    refresh_interval = 900  # Tiempo en segundos
    time.sleep(refresh_interval)
    st.rerun()
