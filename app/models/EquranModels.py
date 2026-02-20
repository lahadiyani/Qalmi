from app.extension import db
from datetime import datetime


class Surah(db.Model):
    __tablename__ = "surah"

    id = db.Column(db.Integer, primary_key=True)
    nomor = db.Column(db.Integer, unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    nama_latin = db.Column(db.String(100))
    arti = db.Column(db.String(150))
    jumlah_ayat = db.Column(db.Integer)
    tempat_turun = db.Column(db.String(50))
    deskripsi = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ayat = db.relationship(
        "Ayat",
        backref="surah",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    tafsir = db.relationship(
        "Tafsir",
        backref="surah",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Ayat(db.Model):
    __tablename__ = "ayat"

    __table_args__ = (
        db.UniqueConstraint("surah_id", "nomor_ayat", name="uq_surah_nomor_ayat"),
    )

    id = db.Column(db.Integer, primary_key=True)

    surah_id = db.Column(
        db.Integer,
        db.ForeignKey("surah.id", ondelete="CASCADE"),
        nullable=False
    )

    nomor_ayat = db.Column(db.Integer, nullable=False)
    teks_arab = db.Column(db.Text)
    teks_latin = db.Column(db.Text)
    teks_indonesia = db.Column(db.Text)
    audio_url = db.Column(db.Text)


class Tafsir(db.Model):
    __tablename__ = "tafsir"

    __table_args__ = (
        db.UniqueConstraint("surah_id", "nomor_ayat", name="uq_tafsir_surah_ayat"),
    )

    id = db.Column(db.Integer, primary_key=True)

    surah_id = db.Column(
        db.Integer,
        db.ForeignKey("surah.id", ondelete="CASCADE"),
        nullable=False
    )

    nomor_ayat = db.Column(db.Integer, nullable=False)
    tafsir = db.Column(db.Text)


class Bookmark(db.Model):
    __tablename__ = "bookmark"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    surah_id = db.Column(
        db.Integer,
        db.ForeignKey("surah.id", ondelete="CASCADE"),
        nullable=False
    )

    nomor_ayat = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    surah_id = db.Column(
        db.Integer,
        db.ForeignKey("surah.id", ondelete="CASCADE"),
        nullable=False
    )

    nomor_ayat = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
