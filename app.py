import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import pytz
from flask import Flask, render_template, request, send_file
import io
from minio import Minio
from config import Config
from models import db, SuratPernyataan
from utils.helpers import decode_signature, safe_filename
from utils.pdf import generate_pdf

#APP INIT
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "static", "Logo_BMKG.png")
LOCAL_TEMP_PDF = os.path.join(BASE_DIR, "pdf_temp")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOCAL_TEMP_PDF, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

#LOGGING
log_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=5 * 1024 * 1024,  
    backupCount=5              
)

log_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler]
)

logging.info("Aplikasi Flask berhasil diinisialisasi")

#MINIO INIT
minio_client = None

try:
    minio_client = Minio(
        Config.MINIO_ENDPOINT,
        access_key=Config.MINIO_ACCESS_KEY,
        secret_key=Config.MINIO_SECRET_KEY,
        secure=Config.MINIO_SECURE
    )

    if not minio_client.bucket_exists(Config.MINIO_BUCKET):
        minio_client.make_bucket(Config.MINIO_BUCKET)

    logging.info("MinIO terhubung | bucket=%s", Config.MINIO_BUCKET)

except Exception:
    logging.exception("MinIO tidak tersedia")

#ROUTES
@app.route("/")
def index():
    logging.info("Halaman form diakses")
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        #MENGAMBIL DATA FORM
        nama = request.form.get("nama", "").strip()
        nip = request.form.get("nip", "").strip()
        instansi = request.form.get("instansi", "").strip()
        kegiatan = request.form.get("kegiatan", "").strip()
        periode = request.form.get("periode", "").strip()
        kota = request.form.get("kota", "Makassar")
        ttd_base64 = request.form.get("ttd_base64", "").strip()

        if not all([nama, nip, instansi, kegiatan, periode]):
            logging.warning("Form tidak lengkap")
            return "Semua field wajib diisi", 400

        #VALIDASI TTD DAN MINIO
        ttd_io = decode_signature(ttd_base64)
        if not ttd_io:
            logging.warning("Tanda tangan tidak valid | nama=%s", nama)
            return "Tanda tangan tidak valid", 400

        if not minio_client:
            logging.error("MinIO belum tersedia")
            return "Storage belum tersedia", 500

        if not os.path.exists(LOGO_PATH):
            logging.error("Logo tidak ditemukan")
            return "Logo tidak ditemukan", 500

        #WAKTU DAN NAMA PDF
        tz = pytz.timezone("Asia/Makassar")
        now = datetime.now(tz)
        tanggal_str = now.strftime("%d %B %Y")
        safe_name = safe_filename(nama)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        pdf_name = f"Surat_Pernyataan_{safe_name}_{timestamp}.pdf"
        pdf_path = os.path.join(LOCAL_TEMP_PDF, pdf_name)
        object_path = f"{now:%Y/%m}/{pdf_name}"

        logging.info("Generate PDF dimulai | nama=%s", nama)

        #GENERATE PDF
        generate_pdf(
            output_path=pdf_path,
            logo_path=LOGO_PATH,
            nama=nama,
            nip=nip,
            instansi=instansi,
            kegiatan=kegiatan,
            periode=periode,
            kota=kota,
            tanggal_str=tanggal_str,
            ttd_io=ttd_io
        )

        #UPLOAD KE MINIO
        minio_client.fput_object(
            Config.MINIO_BUCKET,
            object_path,
            pdf_path,
            content_type="application/pdf"
        )

        pdf_url = minio_client.presigned_get_object(
            Config.MINIO_BUCKET,
            object_path,
            expires=timedelta(minutes=10)
        )

        os.remove(pdf_path)

        logging.info(
            "PDF berhasil diupload | object=%s",
            object_path
        )

        #SIMPAN DATABASE
        data = SuratPernyataan(
            nama=nama,
            nip=nip,
            instansi=instansi,
            kegiatan=kegiatan,
            periode=periode,
            pdf_object=object_path,
            created_at=now
        )

        db.session.add(data)
        db.session.commit()

        logging.info(
            "Data tersimpan ke DB | nama=%s | nip=%s",
            nama, nip
        )

        return render_template("preview.html", pdf_url=pdf_url, surat_id=data.id)

    except Exception:
        logging.exception("Terjadi kesalahan saat generate PDF")
        return "Terjadi kesalahan server", 500

@app.route("/download/<int:surat_id>")
def download_pdf(surat_id):
    try:
        data = SuratPernyataan.query.get_or_404(surat_id)

        response = minio_client.get_object(
            Config.MINIO_BUCKET,
            data.pdf_object
        )

        file_data = response.read()
        response.close()
        response.release_conn()

        filename = os.path.basename(data.pdf_object)

        logging.info(
            "Download PDF | id=%s | file=%s",
            surat_id, filename
        )

        return send_file(
            io.BytesIO(file_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception:
        logging.exception(
            "Gagal download PDF | id=%s",
            surat_id
        )
        return "Gagal mengunduh file", 500

#RUN APP
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


