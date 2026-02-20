import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    raw_uri = os.getenv('DATABASE_URI') or "sqlite:///database/data.db"

    if raw_uri.startswith("sqlite:///"):
        relative_path = raw_uri.replace("sqlite:///", "")
        abs_db_path = os.path.join(basedir, relative_path)

        db_dir = os.path.dirname(abs_db_path)
        os.makedirs(db_dir, exist_ok=True)

        SQLALCHEMY_DATABASE_URI = "sqlite:///" + abs_db_path
    else:
        SQLALCHEMY_DATABASE_URI = raw_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_URL = os.getenv('EQURAN_API_URL')
