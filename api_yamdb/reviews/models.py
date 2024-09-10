from django.core.validators import (MaxValueValidator, MinValueValidator)
from django.db import models

from users.models import User
from .validators import validate_year


class CommonGenreCat(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        abstract = True
        verbose_name = 'Абстрактная модель'
        verbose_name_plural = 'Абстрактная модель'

    def __str__(self):
        return self.name


class Genre(CommonGenreCat):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(CommonGenreCat):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название")
    year = models.PositiveSmallIntegerField(null=True, blank=True,
                                            validators=[validate_year],
                                            verbose_name="Год выпуска")
    description = models.TextField(blank=True, null=True,
                                   verbose_name="Описание")
    category = models.ForeignKey('Category', on_delete=models.DO_NOTHING,
                                 related_name='titles',
                                 verbose_name="Категория")
    genre = models.ManyToManyField('Genre', verbose_name="Жанры")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Нельзя оценить ниже 1'),
            MaxValueValidator(10, 'Нельзя оценить выше 10'),
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateField(
        auto_now_add=True, db_index=True, verbose_name='Дата публикации')

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
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв'
    )
    pub_date = models.DateField(
        auto_now_add=True, db_index=True, verbose_name='Дата публикации')

    class Meta:
        ordering = ['id']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
