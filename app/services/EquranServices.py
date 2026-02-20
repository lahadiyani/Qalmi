import time
import requests
import json
from functools import lru_cache
from urllib.parse import quote
from config.config import Config
from app.models.EquranModels import Surah, Ayat, Tafsir
from app.extension import db

from app.logger import logger

BASE_URL = (Config.API_URL or "https://equran.id/api/v2").rstrip('/')
DEFAULT_TIMEOUT = 10

class EQuranAPIError(Exception):
    pass

class EQuranService:

    # ----------------------
    # Low level fetch util
    # ----------------------
    @staticmethod
    def _get(endpoint: str, retry: int = 3):
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = f"{BASE_URL}{endpoint}"
        for attempt in range(retry):
            try:
                logger.debug(f"Fetching URL: {url}, attempt {attempt + 1}")
                resp = requests.get(url, timeout=DEFAULT_TIMEOUT)
                resp.raise_for_status()
                json_data = resp.json()
                if not json_data:
                    logger.error(f"No data returned from {url}")
                    raise EQuranAPIError(f"No data returned from {url}")
                logger.info(f"Successfully fetched data from {url}")
                return json_data
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retry - 1:
                    time.sleep(1)
                    continue
                logger.error(f"All attempts failed for {url}", exc_info=True)
                raise EQuranAPIError(f"Failed to fetch {url}: {e}") from e

    # cache daftar surah
    @staticmethod
    @lru_cache(maxsize=1)
    def _fetch_all_surah_raw():
        logger.debug("Fetching all surah raw data")
        resp = EQuranService._get("/surat")
        return resp.get("data", [])

    # ----------------------
    # Normalizer helpers
    # ----------------------
    @staticmethod
    def _first(*args):
        """Return first non-None value from args"""
        for v in args:
            if v is not None:
                return v
        return None

    @staticmethod
    def _to_int(v, default=None):
        try:
            return int(v)
        except Exception:
            return default

    @staticmethod
    def _normalize_ayat_from_api(ay, idx=None):
        """
        Normalize ay object coming from external API (handles different key names).
        Returns dict with keys: nomor, arab, latin, indonesia, audio (object)
        """
        if not ay:
            return {
                "nomor": idx + 1 if idx is not None else None,
                "arab": "",
                "latin": "",
                "indonesia": "",
                "audio": {}
            }

        nomor = EQuranService._first(
            ay.get("nomor"),
            ay.get("nomorAyat"),
            ay.get("number"),
            ay.get("nomor_ayat"),
            idx + 1 if idx is not None else None
        )
        nomor = EQuranService._to_int(nomor, default=(idx + 1 if idx is not None else None))

        arab = EQuranService._first(ay.get("arab"), ay.get("teksArab"), ay.get("text"), "")
        latin = EQuranService._first(ay.get("latin"), ay.get("teksLatin"), ay.get("teks_latin"), ay.get("transliteration"), "")
        indonesia = EQuranService._first(ay.get("indonesia"), ay.get("teksIndonesia"), ay.get("translation"), ay.get("indonesia_text"), "")

        audio = ay.get("audio") or ay.get("audio_url") or ay.get("audioUrl") or {}
        # if audio stored as string, try parse
        if isinstance(audio, str):
            try:
                audio = json.loads(audio)
            except Exception:
                logger.debug("audio is string but not json, leaving empty object")
                audio = {}

        if not isinstance(audio, dict):
            audio = {}

        return {
            "nomor": nomor,
            "arab": arab,
            "latin": latin,
            "indonesia": indonesia,
            "audio": audio
        }

    @staticmethod
    def _normalize_ayat_from_db(ayat_model):
        """
        Normalize ayat row from DB (Ayat model).
        Expects ayat_model has attributes: nomor_ayat, teks_arab, teks_latin, teks_indonesia, audio_url (json string).
        """
        if not ayat_model:
            return {"nomor": None, "arab": "", "latin": "", "indonesia": "", "audio": {}}

        nomor = EQuranService._to_int(getattr(ayat_model, "nomor_ayat", None), default=None)
        arab = getattr(ayat_model, "teks_arab", "") or ""
        latin = getattr(ayat_model, "teks_latin", "") or ""
        indo = getattr(ayat_model, "teks_indonesia", "") or ""

        audio_obj = {}
        audio_raw = getattr(ayat_model, "audio_url", None)
        if audio_raw:
            # audio might already be JSON string
            if isinstance(audio_raw, str):
                try:
                    audio_obj = json.loads(audio_raw)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse audio JSON for ayat {nomor}, raw: {audio_raw}")
                    audio_obj = {}
            elif isinstance(audio_raw, dict):
                audio_obj = audio_raw
            else:
                audio_obj = {}

        return {
            "nomor": nomor,
            "arab": arab,
            "latin": latin,
            "indonesia": indo,
            "audio": audio_obj
        }

    @staticmethod
    def _normalize_surah_meta(data):
        """
        Normalize surah-level fields from API or DB-derived dict.
        """
        nomor = EQuranService._to_int(
            EQuranService._first(
                data.get("nomor") if isinstance(data, dict) else None,
                data.get("number") if isinstance(data, dict) else None,
                data.get("nomorSurah") if isinstance(data, dict) else None
            ),
            default=None
        )

        nama = EQuranService._first(data.get("nama"), data.get("name"), data.get("namaArab"), "")
        nama_latin = EQuranService._first(data.get("nama_latin"), data.get("namaLatin"), data.get("namaLatinText"), "")
        return {"nomor": nomor, "nama": nama or "", "nama_latin": nama_latin or ""}

    # ----------------------
    # Public API methods
    # ----------------------
    @staticmethod
    def get_all_surah(page=1, limit=20, search=None):
        try:
            data = EQuranService._fetch_all_surah_raw()
            if search:
                s_lower = search.lower()
                data = [s for s in data if s_lower in (s.get("namaLatin") or s.get("nama_latin") or "").lower() or s_lower in (s.get("arti") or s.get("meaning") or "").lower()]
            total = len(data)
            start = (page - 1) * limit
            end = start + limit
            logger.info(f"Retrieved {len(data[start:end])} surah(s) for page {page}")
            return {
                "items": data[start:end],
                "meta": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            }
        except Exception as e:
            logger.error("Error in get_all_surah", exc_info=True)
            raise

    @staticmethod
    def get_surah_detail(nomor, page=1, limit=20):
        """
        Return normalized surah detail:
        {
          "nomor": int,
          "nama": str,
          "nama_latin": str,
          "ayat": [...],
          "meta": {"total_ayat": int}
        }
        Handles:
         - data from DB (Ayat rows)
         - data from external API
        """
        try:
            # try DB first
            surah_model = Surah.query.filter_by(nomor=nomor).first()

            if surah_model:
                # DB path
                ayat_query = Ayat.query.filter_by(surah_id=surah_model.id).order_by(Ayat.nomor_ayat)
                total = ayat_query.count()
                # pagination
                ayat_rows = ayat_query.offset((page - 1) * limit).limit(limit).all()
                logger.info(f"Retrieved surah {nomor} from DB with {total} ayat (returning {len(ayat_rows)})")

                processed_ayat = [EQuranService._normalize_ayat_from_db(a) for a in ayat_rows]

                surah_data = {
                    "nomor": surah_model.nomor,
                    "nama": surah_model.nama or "",
                    "nama_latin": surah_model.nama_latin or "",
                    "ayat": processed_ayat,
                    "meta": {"total_ayat": total}
                }
                return surah_data

            # not in DB -> fetch from external API
            raw = EQuranService._get(f"/surat/{nomor}")
            data = raw.get("data") if isinstance(raw, dict) else raw
            if not data:
                logger.warning(f"No data returned for surah {nomor} from API")
                raise EQuranAPIError(f"No data for surah {nomor}")

            logger.info(f"Fetched surah {nomor} from API")

            # normalize surah meta
            surah_meta = EQuranService._normalize_surah_meta(data)

            # ayat raw list (handle different key names)
            ayat_raw_list = data.get("ayat") or data.get("verses") or data.get("items") or []

            # build formatted ayat list (no pagination for API response saved below; but we'll paginate the returned list)
            formatted_ayat_all = []
            for i, ay in enumerate(ayat_raw_list):
                formatted_ayat_all.append(EQuranService._normalize_ayat_from_api(ay, idx=i))

            total_ayat = len(formatted_ayat_all)

            # persist to DB if not exists (best-effort)
            try:
                # create Surah record if missing
                new_surah = Surah.query.filter_by(nomor=surah_meta["nomor"]).first()
                if not new_surah:
                    new_surah = Surah(
                        nomor=surah_meta["nomor"],
                        nama=surah_meta["nama"],
                        nama_latin=surah_meta["nama_latin"],
                        arti=data.get("arti") or data.get("meaning") or "",
                        jumlah_ayat=total_ayat,
                        tempat_turun=data.get("tempatTurun") or data.get("revelation") or ""
                    )
                    db.session.add(new_surah)
                    db.session.flush()
                    # save ayat rows
                    for ay in formatted_ayat_all:
                        audio_json = json.dumps(ay.get("audio") or {}) if ay.get("audio") is not None else "{}"
                        db.session.add(Ayat(
                            surah_id=new_surah.id,
                            nomor_ayat=ay.get("nomor"),
                            teks_arab=ay.get("arab"),
                            teks_latin=ay.get("latin"),
                            teks_indonesia=ay.get("indonesia"),
                            audio_url=audio_json
                        ))
                    db.session.commit()
                    logger.info(f"Saved surah {nomor} and {len(formatted_ayat_all)} ayat to DB")
            except Exception as db_exc:
                logger.exception(f"Failed to persist surah {nomor} to DB (continuing): {db_exc}")
                # do not fail response if DB persist fails

            # paginate the formatted_ayat_all for return
            start = (page - 1) * limit
            end = start + limit
            paged = formatted_ayat_all[start:end]

            surah_result = {
                "nomor": surah_meta["nomor"],
                "nama": surah_meta["nama"],
                "nama_latin": surah_meta["nama_latin"],
                "ayat": paged,
                "meta": {"total_ayat": total_ayat}
            }
            return surah_result

        except Exception as e:
            logger.error(f"Error in get_surah_detail for surah {nomor}", exc_info=True)
            raise

    @staticmethod
    def get_tafsir(nomor, ayat=None):
        try:
            surah_model = Surah.query.filter_by(nomor=nomor).first()
            tafsir_list = []

            # Ambil dari DB jika ada
            if surah_model:
                query = Tafsir.query.filter_by(surah_id=surah_model.id)
                if ayat:
                    try:
                        query = query.filter_by(nomor_ayat=int(ayat))
                    except ValueError:
                        pass
                tafsir_rows = query.all()
                if tafsir_rows:
                    logger.info(f"Retrieved tafsir for surah {nomor} from DB")
                    return {
                        "nomor": surah_model.nomor,
                        "nama": surah_model.nama,
                        "tafsir": [{"ayat": t.nomor_ayat, "tafsir": t.tafsir} for t in tafsir_rows]
                    }

            # Fetch dari API
            raw = EQuranService._get(f"/tafsir/{nomor}")
            data = raw.get("data") if isinstance(raw, dict) else raw
            tafsir_data = data.get("tafsir", []) if isinstance(data, dict) else (data or [])

            # Simpan ke DB (best-effort)
            if tafsir_data:
                try:
                    if not surah_model:
                        surah_model = Surah.query.filter_by(nomor=nomor).first()
                    for item in tafsir_data:
                        db.session.merge(Tafsir(
                            surah_id=surah_model.id if surah_model else None,
                            nomor_ayat=item.get("ayat"),
                            tafsir=item.get("teks") or item.get("tafsir") or item.get("text") or ""
                        ))
                    db.session.commit()
                    logger.info(f"Saved tafsir for surah {nomor} to DB")
                except Exception as db_exc:
                    logger.exception(f"Failed to persist tafsir for surah {nomor} (continuing): {db_exc}")

            # Filter per ayat jika dibutuhkan
            if ayat:
                try:
                    tafsir_data = [t for t in tafsir_data if t.get("ayat") == int(ayat)]
                except ValueError:
                    pass

            return {
                "nomor": nomor,
                "nama": surah_model.nama if surah_model else None,
                "tafsir": tafsir_data
            }
        except Exception as e:
            logger.error(f"Error in get_tafsir for surah {nomor}", exc_info=True)
            raise

    @staticmethod
    def generate_audio_url(surah, ayat=None):
        surah_str = quote(str(surah))
        audio_url = f"{BASE_URL}/audio/{surah_str}.mp3" if not ayat else f"{BASE_URL}/audio/{surah_str}/{quote(str(ayat))}.mp3"
        logger.debug(f"Generated audio URL: {audio_url}")
        return {"audio_url": audio_url}

    @staticmethod
    def clear_surah_cache():
        EQuranService._fetch_all_surah_raw.cache_clear()
        logger.info("Cleared surah cache")
