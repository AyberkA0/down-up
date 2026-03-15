import requests
from datetime import datetime, timezone
import uuid
import time

# --- Constants ---
API_URL = "https://*.com"
REGISTER_ENDPOINT = "/register_user"
ADD_DATA_ENDPOINT = "/add_data"
GET_DATA_ENDPOINT = "/get_data"
DEBUG_LOG_ENDPOINT = "/debug_log"

def debug_log(message):
    response = requests.post(API_URL + DEBUG_LOG_ENDPOINT, json={
        "message": message
    }, timeout=5)
    return response.status_code

def register(role):
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    response = requests.post(API_URL + REGISTER_ENDPOINT, json={
        "user_id": user_id,
        "created_at": created_at,
        "role": role
    }, timeout=10)

    return response.status_code, user_id

def update_last_online(user_id, page=None):
    last_online = datetime.now(timezone.utc).isoformat()

    page.client_storage.set("last_online", last_online)

    try:
        resp = requests.post(
            API_URL + ADD_DATA_ENDPOINT,
            json={
                "user_id": user_id,
                "data_key": "last_online",
                "data_value": last_online
            },
            timeout=10
        )
        return resp.status_code
    except requests.RequestException:
        return 0

def _parse_iso(s: str | None):
    if not s:
        return None
    try:
        s = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def is_last_online_today(page, user_id: str | None = None) -> bool:
    if page is None or not getattr(page, "client_storage", None):
        return False

    try:
        last_iso = page.client_storage.get("last_online")
        if not last_iso:
            return False

        last_dt = _parse_iso(last_iso)
        if last_dt is None:
            return False

        created_dt = None

        if user_id:
            try:
                r = requests.get(
                    API_URL + GET_DATA_ENDPOINT,
                    params={"user_id": user_id, "data_key": "created_at"},
                    timeout=5,
                )
                if r.status_code == 200:
                    created_dt = _parse_iso(r.json().get("created_at"))
            except requests.RequestException:
                pass

        if created_dt is None:
            created_dt = _parse_iso(page.client_storage.get("created_at"))

        if created_dt is not None:
            delta_sec = abs((last_dt.astimezone(timezone.utc) - created_dt.astimezone(timezone.utc)).total_seconds())
            if delta_sec < 180:
                return False

        local_dt = last_dt.astimezone()
        today_local = datetime.now().date()
        return local_dt.date() == today_local

    except Exception as e:
        print(f"[DEBUG] Beklenmeyen hata: {e}")
        return False
    
def add_action(user_id: str, action: tuple | list) -> int:
    now = datetime.now()
    ts_ms = int(now.timestamp() * 1000)

    data_key = f"actions.{ts_ms}"
    data_value = list(action)

    try:
        resp = requests.post(
            API_URL + ADD_DATA_ENDPOINT,
            json={
                "user_id": user_id,
                "data_key": data_key,
                "data_value": data_value
            },
            timeout=10
        )

        return resp.status_code
    except requests.RequestException:
        return 0
    
def get_actions(user_id: str):
    try:
        resp = requests.get(
            API_URL + GET_DATA_ENDPOINT,
            params={"user_id": user_id},
            timeout=10
        )
        if resp.status_code != 200:
            print(f"[DEBUG] get_actions başarısız: status={resp.status_code}")
            return []

        data = resp.json()
        actions = data.get("actions", {})

        result = []
        for ts, val in actions.items():
            try:
                ts_int = int(ts)
            except ValueError:
                ts_int = ts
            action_tuple = tuple(val) if isinstance(val, (list, tuple)) else (val,)
            result.append((ts_int, action_tuple))

        result.sort(key=lambda x: x[0])
        return result
    except Exception as e:
        print(f"[DEBUG] get_actions hatası: {e}")

def is_user_id_valid(user_id: str):
    if not user_id:
        return False

    try:
        r = requests.get(
            API_URL + GET_DATA_ENDPOINT,
            params={"user_id": user_id, "data_key": "created_at"},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            return "created_at" in data

        return False

    except requests.RequestException as e:
        print(f"[DEBUG] is_user_id_valid request error: {e}")
        return False
    
def check_server():
    try:
        r = requests.get(API_URL, timeout=3)
        r.raise_for_status()
        data = r.json()
        return data.get("status")
    except (requests.RequestException, ValueError):
        return False
    
def check_internet():
    try:
        r = requests.get("https://clients3.google.com/generate_204", timeout=3)
        return r.status_code == 204
    except Exception:
        return False
