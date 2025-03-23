def telegram_user(request):
    """
    Добавляет информацию о пользователе Telegram в контекст всех шаблонов
    """
    if request.user.is_authenticated:
        return {
            'telegram_user': request.user,
            'telegram_photo': request.user.photo_url or None,
        }
    return {
        'telegram_user': None,
        'telegram_photo': None,
    }