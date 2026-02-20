# app/extension.py

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inisialisasi tanpa app (application factory pattern friendly)
cors = CORS()
db = SQLAlchemy()
migrate = Migrate()
