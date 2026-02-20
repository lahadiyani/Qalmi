import logging
from logging.handlers import RotatingFileHandler
import os

# Buat folder logs jika belum ada
os.makedirs("logs", exist_ok=True)

# Logger utama
logger = logging.getLogger("EQuranLogger")
logger.setLevel(logging.DEBUG)  # Tangkap semua level log

# RotatingFileHandler agar file tidak membesar tak terkendali
file_handler = RotatingFileHandler(
    "logs/data.log", maxBytes=5*1024*1024, backupCount=5  # 5MB per file, simpan 5 backup
)
file_handler.setLevel(logging.DEBUG)

# Format log
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Optional: tampilkan juga di console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
