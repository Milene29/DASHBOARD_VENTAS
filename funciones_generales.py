import datetime
import pytz
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd


def fecha_peru_hoy():
    lima_timezone = pytz.timezone('America/Lima')
    lima_time = datetime.datetime.now(lima_timezone)
    return lima_time.date()
def autenticar_drive():
    gauth = GoogleAuth()
    # Cargar credenciales desde mycreds.txt
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None or gauth.access_token_expired:
        # Si no hay credenciales o han expirado, autenticación manual
        gauth.LocalWebserverAuth()  
        gauth.SaveCredentialsFile("mycreds.txt")
    else:
        gauth.Authorize()

    drive = GoogleDrive(gauth)
    service = build('drive', 'v3', credentials=gauth.credentials)
    return service

def descargar_archivo_drive(file_id):
    service = autenticar_drive()

    # Exportar archivo Google Sheets como Excel (XLSX)
    request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_bytes = io.BytesIO()
    downloader = MediaIoBaseDownload(file_bytes, request)
    done = False

    while not done:
        status, done = downloader.next_chunk()

    # Cargar contenido del Excel en un DataFrame de pandas
    file_bytes.seek(0)
    df = pd.read_excel(file_bytes, engine='openpyxl')
    return df