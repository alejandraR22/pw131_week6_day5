from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .models import db,User


migrate = Migrate()
login_manager = LoginManager()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).one_or_none()

from .auth import auth_bp
app.register_blueprint(auth_bp)

from .pokemon import pokemon_bp
app.register_blueprint(pokemon_bp)

from .site import site_bp
app.register_blueprint(site_bp)




    