from flask import render_template
from . import site_bp as site


@site.route("/")
def index():
    return render_template('index.html')
