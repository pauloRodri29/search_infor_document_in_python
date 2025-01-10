from flask import Flask

app = Flask(__name__, template_folder='extracao_dados/templates', static_folder='extracao_dados/static')

from extracao_dados.view import *
if __name__ == "__main__":
    app.run(debug=True)