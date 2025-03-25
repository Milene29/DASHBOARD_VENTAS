
import subprocess
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import pytz
import locale
import os

def prometeo_auth_user(session, url, user, password):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    data = {
        "ScriptManager1": "UpdatePanel1|btnIngresar",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": "C2EE9ABB",
        "txtUsuario": user,
        "txtClave": password,
        "btnIngresar": "Ingresar"
    }

    # Headers for the POST request
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "X-MicrosoftAjax": "Delta=true",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Origin": "https://prometeo.ieduca.pe",
        "Referer": "https://prometeo.ieduca.pe/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1",
        "TE": "trailers"
    }
    print("Ingresando a Prometeo..")

    response_post = session.post(url, data=data, headers=headers)

def crear_carpeta_si_no_existe(ruta: Path):
    if not ruta.exists():
        print(f"Creando la carpeta: {ruta}")
        ruta.mkdir(parents=True, exist_ok=True)


def prometeo_download_report(session, url, init_date, end_date, destination: Path):
    crear_carpeta_si_no_existe(destination)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        
    data = {
        "ctl00$TxtClave": "",
        "ctl00$ContentPlaceHolder1$ddlCampania": "0",
        "ctl00$ContentPlaceHolder1$ddlEvento": "0",
        "ctl00$ContentPlaceHolder1$ddlProyecto": "0",
        "ctl00$ContentPlaceHolder1$DdlSexo": "0",
        "ctl00$ContentPlaceHolder1$txtFechaInicio": init_date,
        "ctl00$ContentPlaceHolder1$txtFechaFin": end_date,
        "ctl00$ContentPlaceHolder1$txtFechaRegistro1": "",
        "ctl00$ContentPlaceHolder1$txtFechaRegistro2": "",
        "ctl00$ContentPlaceHolder1$GvTipoAtencion$ctl08$ChkTipoAtencionG": "on",
        "ctl00$ContentPlaceHolder1$GvTipoAtencion$ctl12$ChkTipoAtencionG": "on",
        "AnioDesde": "0",
        "AnioHasta": "0",
        "ctl00$ContentPlaceHolder1$imgExportarSeguimiento.x": "0",
        "ctl00$ContentPlaceHolder1$imgExportarSeguimiento.y": "0",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE" : viewstate,
        "__VIEWSTATEGENERATOR": "F801A079"
    }

# Set the headers
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://prometeo.ieduca.pe",
        "Connection": "keep-alive",
        "Referer": "https://prometeo.ieduca.pe/Reportes/ReporteSeguimiento.aspx",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "Priority": "u=0, i",
    }

    report_name = "corte_del_dia.xls"
    print("Descargando archivo...")
    response_post = session.post(url, data=data, headers=headers)
    with open(destination / report_name, 'wb') as file:
        file.write(response_post.content) 
    












def lima_current_datetime():
    lima_time_zone = pytz.timezone('America/Lima')
    return datetime.now(lima_time_zone)

def get_curr_lima_diasem():
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    return lima_current_datetime().strftime('%A')

def get_curr_lima_hour():
    return lima_current_datetime().hour

def get_curr_date_lima_filename():
    return lima_current_datetime().strftime('%Y%m%d')





if __name__ == '__main__':
    s = requests.Session()
    print(lima_current_datetime().strftime("%d/%m/%Y"))
    prometeo_auth_user(s, "https://prometeo.ieduca.pe", "MGARRIDOUCALPRE", "Admin@24")
    dest = Path("./reporte_prometeo/")
    
    prometeo_download_report(s,"https://prometeo.ieduca.pe/Reportes/ReporteSeguimiento.aspx", lima_current_datetime().strftime("%d/%m/%Y"), lima_current_datetime().strftime("%d/%m/%Y"), dest)
   

