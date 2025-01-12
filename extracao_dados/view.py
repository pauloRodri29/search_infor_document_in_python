from run import app
import os

from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'  # Create a dedicated folder for uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def view_home():
    # Load files from the upload directory
    files_uploads = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", files_uploads=files_uploads)

@app.route("/upload", methods=["POST"])
def upload():
    for file in request.files.getlist("file"):  # Use getlist to handle multiple files
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
    # Don't pass files_uploads in redirect, update it in view_home
    return redirect(url_for('view_home'))

@app.route("/delete/<filename>")
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass  # Ignore if file doesn't exist
    return redirect(url_for('view_home'))

@app.route("/dados_extraidos")
def dados_extraidos():
    request.files.clear()
    return render_template("extracao_dados.html")