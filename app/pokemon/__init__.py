from flask import Blueprint
pokemon_bp= Blueprint("pokemon", __name__)
from . import routes


