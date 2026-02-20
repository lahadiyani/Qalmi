from app.blueprints import api
from app.controllers.EquranControllers import QuranController

# =========================================================
# SURAH
# =========================================================

@api.route("/surah", methods=["GET"])
def list_surah():
    """List all surah with optional pagination & search"""
    return QuranController.list_surah()


@api.route("/surah/<int:nomor>", methods=["GET"])
def detail_surah(nomor):
    """Get surah detail by nomor with ayat pagination"""
    return QuranController.detail_surah(nomor)


# =========================================================
# TAFSIR
# =========================================================

@api.route("/tafsir/<int:nomor>", methods=["GET"])
def tafsir_surah(nomor):
    """Get tafsir for a surah or specific ayat"""
    return QuranController.tafsir_surah(nomor)


# =========================================================
# AUDIO
# =========================================================

@api.route("/audio", methods=["GET"])
def get_audio():
    """Get audio URL for a surah or specific ayat"""
    return QuranController.get_audio()


# =========================================================
# BOOKMARK (Auth Required)
# =========================================================

@api.route("/bookmark", methods=["POST"])
def add_bookmark():
    """Add a bookmark for the authenticated user"""
    return QuranController.add_bookmark()


@api.route("/bookmark", methods=["DELETE"])
def remove_bookmark():
    """Remove a bookmark for the authenticated user"""
    return QuranController.remove_bookmark()


@api.route("/bookmark", methods=["GET"])
def list_bookmark():
    """List all bookmarks for the authenticated user"""
    return QuranController.list_bookmark()


# =========================================================
# NOTES
# =========================================================

@api.route("/note", methods=["POST"])
def save_note():
    """Save a note for a specific surah and ayat"""
    return QuranController.save_note()


@api.route("/note", methods=["GET"])
def get_note():
    """Get a note for a specific surah and ayat"""
    return QuranController.get_note()

@api.route("/surah/cache/clear", methods=["POST"])
def clear_surah_cache():
    """Clear cached surah data"""
    return QuranController.clear_surah_cache()
