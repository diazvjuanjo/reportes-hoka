from flask import Flask, request, jsonify
from flask_cors import CORS  # Permitir solicitudes CORS
import os
import json
import gspread
import tempfile  # Para manejar archivos temporales correctamente
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app, origins=["https://www.comercialudra.es"])  # Permitir solo solicitudes desde tu dominio

# Configurar permisos de Google Drive y Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Cargar credenciales de Google
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    CREDS = Credentials.from_service_account_info(
        json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")), scopes=SCOPES
    )
else:
    CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

# Configurar Google Sheets y Google Drive
GOOGLE_SHEET_ID = "1vtn6KNXqE7c1qETN7GN6cUIO5cfeQmG419u-XPWnTfQ"  # ID de la hoja de cálculo
GOOGLE_DRIVE_FOLDER_ID = "1GM95-idW7Sq-MIja8NhtkrUGE-dTkbLk"  # ID de la carpeta en Google Drive

# Autenticar con Google Sheets
client = gspread.authorize(CREDS)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1  # Accede a la primera hoja

# Autenticar con Google Drive
drive_service = build("drive", "v3", credentials=CREDS)

@app.route("/submit-form", methods=["POST"])
def submit_form():
    try:
        # Obtener datos del formulario
        name = request.form.get("name")
        cif = request.form.get("cif")
        month = request.form.get("month")
        year = request.form.get("year")
        road_rank = request.form.get("road-rank")
        trail_rank = request.form.get("trail-rank")

        # Obtener datos del ranking de carretera y trail
        top1_carretera = request.form.get("top1")
        top2_carretera = request.form.get("top2")
        top3_carretera = request.form.get("top3")
        other1 = request.form.get("other1", "")
        other2 = request.form.get("other2", "")
        other3 = request.form.get("other3", "")

        top1_trail = request.form.get("top4")
        top2_trail = request.form.get("top5")
        top3_trail = request.form.get("top6")
        other4 = request.form.get("other4", "")
        other5 = request.form.get("other5", "")
        other6 = request.form.get("other6", "")

        observations = request.form.get("observations", "")

        # Manejo de archivos
        file = request.files.get("document")
        file_link = "No adjunto"

        if file:
            # ✅ Guardar temporalmente el archivo
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            # ✅ Subir el archivo a Google Drive
            file_metadata = {
                "name": file.filename,
                "parents": [GOOGLE_DRIVE_FOLDER_ID]
            }
            media = MediaFileUpload(temp_file_path, mimetype=file.content_type)
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

            # ✅ Obtener el enlace de descarga del archivo
            file_link = f"https://drive.google.com/file/d/{uploaded_file['id']}/view?usp=drivesdk"

            # ✅ Eliminar el archivo temporal después de subirlo
            os.remove(temp_file_path)

        # Guardar los datos en Google Sheets
        sheet.append_row([
            name, cif, month, year, road_rank, trail_rank, 
            top1_carretera, top2_carretera, top3_carretera, other1, other2, other3,
            top1_trail, top2_trail, top3_trail, other4, other5, other6,
            observations, file_link
        ])

        return jsonify({
            "status": "success",
            "message": "Formulario enviado correctamente.",
            "file_link": file_link
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
