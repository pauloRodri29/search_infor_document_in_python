from lib.main import app
@app.route("/")
def view_home():
    return "Hello, World!"
