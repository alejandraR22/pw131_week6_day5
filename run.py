from app import app
from app import create_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


    