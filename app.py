from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "base para preparar el docker"

if __name__ == "__main__":
    app.run()