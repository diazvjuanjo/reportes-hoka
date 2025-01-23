from flask import Flask, request, jsonify
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import gspread

app = Flask(__name__)

# Configuración de Google APIs
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDS = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

# Inicializar Google Sheets
sheet_service = gspread.authorize(CREDS)
SHEET_NAME = "Reportes Hoka"

# Ruta de subida de archivos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/submit-form", methods=["POST"])
def submit_form():
    try:
        # Obtener datos del formulario
        data = request.form
        file = request.files['document']

        # Guardar el archivo temporalmente
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Subir el archivo a Google Drive
        drive_service = build('drive', 'v3', credentials=CREDS)
        file_metadata = {'name': file.filename, 'parents': ['1GM95-idW7Sq-MIja8NhtkrUGE-dTkbLk']}
        media = MediaFileUpload(file_path, resumable=True)
        file_drive = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        file_link = file_drive.get('webViewLink')

        # Guardar datos en Google Sheets
        sheet = sheet_service.open(SHEET_NAME)
        cif = data['cif']

        # Verificar si existe una hoja para este CIF
        try:
            worksheet = sheet.worksheet(cif)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=cif, rows=100, cols=20)

        # Agregar datos al Google Sheets
        worksheet.append_row([
            data['month'],
            data['year'],
            data['hoka-rank'],
            data['road-rank'],
            data['trail-rank'],
            file_link
        ])

        return jsonify({"status": "success", "message": "Formulario enviado correctamente."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
