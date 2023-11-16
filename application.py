from flask import Flask
from flask_cors import CORS
from blueprints.manage.views import manage
from blueprints.auth.views import auth
from blueprints.assignment.views import assignment
from blueprints.employee.views import employee


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config["SECRET_KEY"] = "secret"
    app.register_blueprint(manage, url_prefix="/manage")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(assignment, url_prefix="/assignments")
    app.register_blueprint(employee, url_prefix="/employees")

    @app.route("/")
    def index():
        return "Hello World!"

    return app
