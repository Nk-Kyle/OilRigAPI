from flask import Flask
from flask_cors import CORS
from blueprints.manage.views import manage
from blueprints.auth.views import auth

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SECRET_KEY"] = "secret"
app.register_blueprint(manage, url_prefix="/manage")
app.register_blueprint(auth, url_prefix="/auth")


# Hello World
@app.route("/")
def hello_world():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
