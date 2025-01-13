from run import app
import os

from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from extracao_dados.utils.extraindo import main

UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', files=os.listdir(app.config['UPLOAD_FOLDER']))

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('file')
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

@app.route('/data_extraction<filename>', methods=['GET', 'POST'])
def extract(filename):
    if filename is None:
        return redirect(url_for('index'))
    else:
        information = main(filename)
        return information

@app.route('/delete/<filename>')
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))