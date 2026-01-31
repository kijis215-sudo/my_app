# app/__init__.py
from flask import Flask
from app.config import Config
import google.generativeai as genai

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure Google Generative AI
    if app.config.get("GOOGLE_GENAI_API_KEY"):
        genai.configure(
            api_key=app.config["GOOGLE_GENAI_API_KEY"],
            client_options={"api_endpoint": "https://generativelanguage.googleapis.com/v1"},
        )

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
