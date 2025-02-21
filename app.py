from flask import Flask
from flask_cors import CORS
from models import db
from routes import auth_bp  # Import Blueprint

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database Configuration
app.config.from_object('config.Config')

# Initialize database with app
db.init_app(app)

# Register authentication Blueprint
app.register_blueprint(auth_bp)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
