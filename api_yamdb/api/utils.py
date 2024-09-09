from django.core.mail import send_mail

from api_yamdb.settings import EMAIl_ADRESS


def send_confirmation_code(email, confirmation_code):
    """Oтправляет на почту пользователя код подтверждения."""
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=EMAIl_ADRESS,
        recipient_list=(email,),
        fail_silently=False,
    )
