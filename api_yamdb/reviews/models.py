from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews' # Соединить с моделью пользователя
    )
    text = models.TextField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews' # Соединить с моделью Title
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments' # Соединить с моделью пользователя.
    )
    text = models.TextField
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
