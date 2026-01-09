from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SuratPernyataan(db.Model):
    __tablename__ = "surat_pernyataan"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    nip = db.Column(db.String(50), nullable=False)
    instansi = db.Column(db.String(150), nullable=False)
    kegiatan = db.Column(db.Text, nullable=False)
    periode = db.Column(db.String(100), nullable=False)
    pdf_object = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<SuratPernyataan {self.nama}>"
