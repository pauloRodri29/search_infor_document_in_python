from run import app

from flask import render_template

@app.route("/")
def view_home():
    return render_template("homepage.html", files_uploads = ["Arquivo 1",'Arquivo 2'])