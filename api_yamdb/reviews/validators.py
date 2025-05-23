from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    if value >= timezone.now().year:
        raise ValidationError('Проверьте год выпуска')
    return value
