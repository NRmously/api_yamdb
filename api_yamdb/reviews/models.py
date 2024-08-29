from django.db import models


# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name='titles')
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    #
    # def __str__(self):
    #     return f'{self.genre} {self.title}'

# Ресурс titles: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
# Ресурс categories: категории (типы) произведений («Фильмы», «Книги», «Музыка»). Одно произведение может быть привязано только к одной категории.
# Ресурс genres: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
# При удалении объекта произведения Title должны удаляться все отзывы к этому произведению и комментарии к ним.
# При удалении объекта категории Category не нужно удалять связанные с этой категорией произведения.
