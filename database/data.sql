PRAGMA foreign_keys = ON;

-- =====================================================
-- SURAH TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS surah (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor INTEGER UNIQUE NOT NULL,
    nama TEXT NOT NULL,
    nama_latin TEXT,
    arti TEXT,
    jumlah_ayat INTEGER,
    tempat_turun TEXT,
    deskripsi TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- AYAT TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS ayat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    surah_id INTEGER NOT NULL,
    nomor_ayat INTEGER NOT NULL,
    teks_arab TEXT,
    teks_latin TEXT,
    teks_indonesia TEXT,
    audio_url TEXT,
    UNIQUE(surah_id, nomor_ayat),
    FOREIGN KEY (surah_id) REFERENCES surah(id) ON DELETE CASCADE
);

-- =====================================================
-- TAFSIR TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS tafsir (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    surah_id INTEGER NOT NULL,
    nomor_ayat INTEGER NOT NULL,
    tafsir TEXT,
    UNIQUE(surah_id, nomor_ayat),
    FOREIGN KEY (surah_id) REFERENCES surah(id) ON DELETE CASCADE
);

-- =====================================================
-- BOOKMARK TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS bookmark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    surah_id INTEGER NOT NULL,
    nomor_ayat INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (surah_id) REFERENCES surah(id) ON DELETE CASCADE
);

-- =====================================================
-- NOTE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    surah_id INTEGER NOT NULL,
    nomor_ayat INTEGER NOT NULL,
    content TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (surah_id) REFERENCES surah(id) ON DELETE CASCADE
);

-- =====================================================
-- INDEXES (Recommended for Performance)
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_ayat_surah ON ayat(surah_id);
CREATE INDEX IF NOT EXISTS idx_tafsir_surah ON tafsir(surah_id);
CREATE INDEX IF NOT EXISTS idx_bookmark_user ON bookmark(user_id);
CREATE INDEX IF NOT EXISTS idx_note_user ON note(user_id);
