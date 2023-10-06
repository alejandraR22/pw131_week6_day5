from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app =Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    return app


if __name__ == "__main__":
    app.run(debug=True)
    