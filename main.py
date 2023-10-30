from flask import Flask
from blueprints.manage.views import manage

app = Flask(__name__)
app.register_blueprint(manage, url_prefix="/manage")

if __name__ == "__main__":
    app.run(debug=True)
