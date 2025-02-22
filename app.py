from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db
from routes import auth_bp  # Import your routes

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS (optional, for frontend communication)
CORS(app)

# Initialize database & migrations
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints (routes)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
