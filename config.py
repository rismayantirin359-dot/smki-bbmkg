import os
from urllib.parse import quote_plus

class Config:
    #DATABASE (MySQL)
    DB_USER = os.getenv("DB_USER", "app_bbmkg")
    DB_PASS = os.getenv("DB_PASS", "AppBbmkg@2025!")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "surat_pernyataan_bbmkg")

    DB_PASS_ENCODED = quote_plus(DB_PASS)

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS_ENCODED}@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #FLASK
    SECRET_KEY = os.getenv("SECRET_KEY", "bbmkg-secret-key-change-this")

    #KONFIGURASI KE MINIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "BMKGADMIN")
    MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "bmkgadmin123")
    MINIO_BUCKET = os.getenv(
        "MINIO_BUCKET",
        "dokumen-pernyataan-menjaga-kerahasiaan"
    )
    MINIO_SECURE = False
