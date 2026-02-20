# app/__init__.py
from flask import Flask
from .extension import db, cors, migrate
from config.config import Config  # import Config dari root

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)  # load config dari config.py

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # <- inisialisasi Flask-Migrate

    from app import models

    with app.app_context():
        db.create_all()

    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
    from .routes.BaseRoutes import main
    from .routes.EquranRoutes import api
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app
