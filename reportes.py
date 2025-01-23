from flask import Flask, request, jsonify
import os
import sqlite3

app = Flask(__name__)

# Configuración de carpeta para guardar archivos subidos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configuración de la base de datos
DATABASE = "reportes.db"

# Crear la base de datos y tabla si no existen
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cif TEXT NOT NULL,
                month TEXT NOT NULL,
                year INTEGER NOT NULL,
                hoka_rank TEXT NOT NULL,
                road_rank TEXT NOT NULL,
                trail_rank TEXT NOT NULL,
                top1 TEXT NOT NULL,
                top2 TEXT NOT NULL,
                top3 TEXT NOT NULL,
                observations TEXT,
                document_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
init_db()

# Ruta para manejar el formulario
@app.route("/submit-form", methods=["POST"])
def submit_form():
    try:
        # Obtener datos del formulario
        data = request.form
        file = request.files["document"]

        # Guardar el archivo subido
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Guardar los datos en la base de datos
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("""
                INSERT INTO reportes (cif, month, year, hoka_rank, road_rank, trail_rank, top1, top2, top3, observations, document_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["cif"],
                data["month"],
                data["year"],
                data["hoka-rank"],
                data["road-rank"],
                data["trail-rank"],
                data["top1"],
                data["top2"],
                data["top3"],
                data.get("observations", ""),  # Observaciones opcionales
                file_path
            ))
        return jsonify({"status": "success", "message": "Formulario enviado correctamente."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Ruta para obtener datos (opcional, para visualizar resultados)
@app.route("/get-data", methods=["GET"])
def get_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reportes")
        rows = cursor.fetchall()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
