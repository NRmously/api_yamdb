from django.contrib import admin
from reviews.models import Category, Genre, Title

# Register your models here.
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
