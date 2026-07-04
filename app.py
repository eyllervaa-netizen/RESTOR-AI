from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug.utils import secure_filename

from image_analyzer import analyze_image


app = Flask(__name__)

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


# ==========================
# KLASÖRLER
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ANALYZED_FOLDER = os.path.join(BASE_DIR, "analyzed")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ANALYZED_FOLDER"] = ANALYZED_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANALYZED_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)



# ==========================
# DOSYA TİPLERİ
# ==========================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )



# ==========================
# ANA SAYFA
# ==========================

@app.route("/")
def index():

    return render_template("index.html")



# ==========================
# FOTOĞRAF ANALİZ
# ==========================

@app.route("/upload", methods=["POST"])
def upload():


    if "photo" not in request.files:

        return "Fotoğraf bulunamadı"



    file = request.files["photo"]


    if file.filename == "":

        return "Fotoğraf seçilmedi"



    if not allowed_file(file.filename):

        return "Desteklenmeyen dosya"



    filename = secure_filename(
        file.filename
    )


    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    file.save(filepath)


    print(
        "Kaydedilen dosya:",
        filepath
    )


    analysis = analyze_image(
        filepath,
        ANALYZED_FOLDER
    )


    return render_template(

        "result.html",

        filename=filename,

        analyzed_image=analysis["image"],

        damage=analysis["damage"],

        material=analysis["material"],

        structure=analysis["structure"],

        risk=analysis["risk"],

        scenario=analysis["scenario"],

        crack_percent=analysis["crack_percent"],

        brightness=analysis["brightness"],

        contrast=analysis["contrast"],

        edge_density=analysis["edge_density"],

        texture_score=analysis["texture_score"],

        recommendation=analysis["recommendation"],

        explanation=analysis["explanation"]

    )



# ==========================
# DOSYA GÖSTER
# ==========================


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )



@app.route("/analyzed/<filename>")
def analyzed_file(filename):

    return send_from_directory(
        ANALYZED_FOLDER,
        filename
    )



@app.route("/reports/<filename>")
def report_file(filename):

    return send_from_directory(
        REPORT_FOLDER,
        filename
    )



# ==========================
# ÇALIŞTIR
# ==========================

if __name__ == "__main__":

    print(">>> YENI APP BASLADI <<<")


    app.run(
        debug=False,
        host="0.0.0.0",
        port=8080
    )