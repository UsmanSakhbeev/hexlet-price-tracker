import hashlib
import hmac
import time

from django.conf import settings


def _build_data_check_string(data: dict[str, str]) -> str:
    parts = []
    for k in sorted(k for k in data.keys() if k != 'hash'):
        v = data[k]
        if v is None:
            continue
        parts.append(f'{k}={v}')
    return '\n'.join(parts)


def verify_telegram_auth(data: dict[str, str], max_age_sec: int = 86400) -> tuple[bool, str]:
    token = settings.TELEGRAM_LOGIN_BOT_TOKEN  # ✅ правильное имя
    if not token:
        return False, "TELEGRAM_LOGIN_BOT_TOKEN не задан"

    tg_hash = data.get('hash')
    if not tg_hash:
        return False, "hash отсутствует"

    data_check_string = _build_data_check_string(data)
    secret_key = hashlib.sha256(token.encode()).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()  # ✅ hexdigest

    if not hmac.compare_digest(calc_hash, tg_hash):
        return False, "Неверная подпись Telegram"

    try:
        auth_date = int(data.get('auth_date', '0'))
    except ValueError:
        return False, "Некорректный auth_date"

    if time.time() - auth_date > max_age_sec:  # ✅ скобки
        return False, "Сессия Telegram устарела"

    return True, 'OK'
