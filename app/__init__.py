from flask import Flask
from flask_cors import CORS

def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    CORS(app)

    # Register the blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
