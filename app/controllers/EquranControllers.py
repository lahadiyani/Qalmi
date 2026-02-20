import json
from flask import jsonify, request, g, Response
from app.services.EquranServices import EQuranService
from app.logger import logger  # Import logger

class QuranController:

    # =========================================================
    # SURAH LIST (with pagination & search)
    # =========================================================
    @staticmethod
    def list_surah():
        try:
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 114))
            search = request.args.get("search")

            logger.debug(f"Listing surah - page: {page}, limit: {limit}, search: {search}")
            result = EQuranService.get_all_surah(page=page, limit=limit, search=search)
            logger.info(f"Returned {len(result.get('items', []))} surah(s)")

            return jsonify({
                "status": "success",
                "data": result
            })
        except Exception as e:
            logger.error("Error in list_surah", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    # =========================================================
    # SURAH DETAIL (with ayat pagination)
    # =========================================================
    @staticmethod
    def detail_surah(nomor):
        try:
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 20))
            logger.debug(f"Fetching detail for surah {nomor} - page {page}, limit {limit}")

            result = EQuranService.get_surah_detail(nomor=nomor, page=page, limit=limit)
            if not result:
                logger.warning(f"No result from service for surah {nomor}")
                return jsonify({"status": "error", "message": "Surah tidak ditemukan"}), 404

            ayat_list = result.get("ayat", []) or []
            normalized = []

            for a in ayat_list:
                # hanya normalisasi ringan — jangan ubah struktur yang valid
                if isinstance(a, dict):
                    # ambil audio dari beberapa kemungkinan key dan parse bila perlu
                    audio_raw = a.get("audio") or a.get("audio_url") or a.get("audioUrl") or {}
                    if isinstance(audio_raw, str):
                        try:
                            audio_obj = json.loads(audio_raw)
                        except Exception:
                            logger.debug(f"audio JSON parse failed for surah {nomor}, ayat {a.get('nomor')}", exc_info=True)
                            audio_obj = {}
                    elif isinstance(audio_raw, dict):
                        audio_obj = audio_raw
                    else:
                        audio_obj = {}

                    normalized.append({
                        "nomor": a.get("nomor") or a.get("nomorAyat") or a.get("number"),
                        "arab": a.get("arab") or a.get("teksArab") or a.get("text") or "",
                        "latin": a.get("latin") or a.get("teksLatin") or a.get("transliteration") or "",
                        "indonesia": a.get("indonesia") or a.get("teksIndonesia") or a.get("translation") or "",
                        "audio": audio_obj
                    })
                else:
                    # jika bukan dict (tak terduga), teruskan apa adanya
                    normalized.append(a)

            result["ayat"] = normalized

            # pastikan ada meta.total_ayat
            meta = result.get("meta") or {}
            if "total_ayat" not in meta:
                meta["total_ayat"] = len(normalized)
            result["meta"] = meta

            logger.info(f"Returned detail for surah {nomor} with {len(normalized)} ayat")
            return jsonify({"status": "success", "data": result})

        except Exception as e:
            logger.error(f"Error in detail_surah for surah {nomor}", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    # =========================================================
    # TAFSIR (per ayat or full surah)
    # =========================================================
    @staticmethod
    def tafsir_surah(nomor):
        try:
            ayat = request.args.get("ayat")
            logger.debug(f"Fetching tafsir for surah {nomor}, ayat {ayat}")
            result = EQuranService.get_tafsir(nomor=nomor, ayat=ayat)
            logger.info(f"Returned tafsir for surah {nomor}")
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error(f"Error in tafsir_surah for surah {nomor}", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    # =========================================================
    # BOOKMARK SYSTEM (User Required)
    # =========================================================
    @staticmethod
    def add_bookmark():
        try:
            user_id = g.user_id
            payload = request.json
            logger.debug(f"User {user_id} adding bookmark: {payload}")
            result = EQuranService.add_bookmark(user_id=user_id, surah=payload.get("surah"), ayat=payload.get("ayat"))
            return jsonify({"status": "success", "message": "Bookmark added", "data": result})
        except Exception as e:
            logger.error("Error in add_bookmark", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    @staticmethod
    def remove_bookmark():
        try:
            user_id = g.user_id
            payload = request.json
            logger.debug(f"User {user_id} removing bookmark: {payload}")
            EQuranService.remove_bookmark(user_id=user_id, surah=payload.get("surah"), ayat=payload.get("ayat"))
            return jsonify({"status": "success", "message": "Bookmark removed"})
        except Exception as e:
            logger.error("Error in remove_bookmark", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    @staticmethod
    def list_bookmark():
        try:
            user_id = g.user_id
            logger.debug(f"Listing bookmarks for user {user_id}")
            result = EQuranService.get_user_bookmarks(user_id)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Error in list_bookmark", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    # =========================================================
    # NOTES SYSTEM
    # =========================================================
    @staticmethod
    def save_note():
        try:
            user_id = g.user_id
            payload = request.json
            logger.debug(f"User {user_id} saving note: {payload}")
            result = EQuranService.save_note(user_id=user_id, surah=payload.get("surah"), ayat=payload.get("ayat"), content=payload.get("content"))
            return jsonify({"status": "success", "message": "Note saved", "data": result})
        except Exception as e:
            logger.error("Error in save_note", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    @staticmethod
    def get_note():
        try:
            user_id = g.user_id
            surah = request.args.get("surah")
            ayat = request.args.get("ayat")
            logger.debug(f"User {user_id} fetching note - surah: {surah}, ayat: {ayat}")
            result = EQuranService.get_note(user_id=user_id, surah=surah, ayat=ayat)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Error in get_note", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500

    # =========================================================
    # AUDIO ACCESS (Optional: Signed URL)
    # =========================================================
    @staticmethod
    def get_audio():
        try:
            surah = request.args.get("surah")
            ayat = request.args.get("ayat")
            logger.debug(f"Generating audio URL for surah {surah}, ayat {ayat}")
            result = EQuranService.generate_audio_url(surah=surah, ayat=ayat)
            return jsonify({"status": "success", "data": result})
        except Exception as e:
            logger.error("Error in get_audio", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 500
        
    @staticmethod
    def clear_surah_cache():
        """Clear cached surah data"""
        try:
            EQuranService.clear_surah_cache()
            return {"status": "success", "message": "Surah cache cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
