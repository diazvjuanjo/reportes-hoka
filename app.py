import os
import json
import gspread
from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Definir los alcances (permisos) para Google Drive y Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Cargar credenciales desde variables de entorno o desde un archivo
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    CREDS = Credentials.from_service_account_info(
        json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")), scopes=SCOPES
    )
else:
    CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

# ID de la carpeta en Google Drive donde se guardarán los archivos
GOOGLE_DRIVE_FOLDER_ID = "1GM95-idW7Sq-MIja8NhtkrUGE-dTkbLk"  # Reemplázalo con tu ID real

# ID de la hoja de Google Sheets donde se guardarán los datos
GOOGLE_SHEET_ID = "1vtn6KNXqE7c1qETN7GN6cUIO5cfeQmG419u-XPWnTfQ"  # Reemplázalo con tu ID real

# Conectar con Google Sheets
client = gspread.authorize(CREDS)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1  # Accede a la primera hoja

@app.route("/submit-form", methods=["POST"])
def submit_form():
    try:
        data = request.form
        file = request.files.get("document")

        # Guardar los datos del formulario en Google Sheets
        sheet.append_row([
            data.get("cif"),
            data.get("month"),
            data.get("year"),
            data.get("road-rank"),
            data.get("trail-rank"),
            data.get("top1"),
            data.get("top2"),
            data.get("top3"),
            data.get("observations")
        ])

        # Subir archivo a Google Drive si existe
        file_link = "No se adjuntó archivo"
        if file:
            file_path = f"/tmp/{file.filename}"
            file.save(file_path)

            drive_service = build("drive", "v3", credentials=CREDS)
            file_metadata = {"name": file.filename, "parents": [GOOGLE_DRIVE_FOLDER_ID]}
            media = MediaFileUpload(file_path, resumable=True)
            uploaded_file = drive_service.files().create(
                body=file_metadata, media_body=media, fields="id, webViewLink"
            ).execute()
            file_link = uploaded_file.get("webViewLink")

        return jsonify({
            "status": "success",
            "message": "Formulario enviado correctamente.",
            "file_link": file_link
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

