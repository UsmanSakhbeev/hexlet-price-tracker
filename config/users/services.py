from django.contrib.auth import get_user_model
from .models import TelegramAccount

User = get_user_model()


def get_or_create_user_from_telegram(tg: dict) -> User:

    try:
        tg_id = int(tg['id'])
    except (KeyError, ValueError):
        raise ValueError('Telegram data must contain numeric "id"')

    tg_username = (tg.get('username') or '').strip()
    first_name = tg.get('first_name') or ''
    last_name = tg.get('last_name') or ''
    photo_url = tg.get('photo_url') or ''

    username = f'tg_{tg_id}'
    email = f'{tg_id}@telegram.local'  # обход unique=True на email

    user, created_user = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'avatar_image': photo_url or '',
        }
    )

    if not created_user and photo_url and not (user.avatar_image
                                               or '').strip():
        user.avatar_image = photo_url
        user.save(update_fields=['avatar_image'])

    link, created_link = TelegramAccount.objects.get_or_create(
        telegram_id=tg_id,
        defaults={
            'user': user,
            'username': tg_username,
            'photo_url': photo_url,
        }
    )

    if not created_link:
        updated = []
        if tg_username and link.username != tg_username:
            link.username = tg_username
            updated.append('username')
        if photo_url and link.photo_url != photo_url:
            link.photo_url = photo_url
            updated.append('photo_url')
        if updated:
            link.save(update_fields=updated)

    return link.user
