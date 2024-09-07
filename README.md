# API YamDB

## Информация о проекте:
Проект YaMDb собирает отзывы пользователей на произведения.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».
Список категорий может быть расширен.

Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»).
Добавлять произведения, категории и жанры может только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.

Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

## Иcпользованные технологии:
Python, Django, Django REST framework, Simple JWT

## Инструкция по установке:
Клонирование репозитория:
```
git clone <https или SSH URL>
```

Создание виртуального окружения и его активация:
```
python -m venv venv
```
```
source venv/bin/activate
```

Обновление менеджера пакетов pip:
```
python -m pip install --upgrade pip
```

Установить зависимости:
```
pip install -r requirements.txt
```

Перейти в директорию с файлом manage.py и выполнить миграции:
```
cd api_yamdb
```
```
python manage.py migrate
```

Создаём супер-пользователя:
```
python manage.py createsuperuser
```

Запуск сервера:
```
python manage.py runserver
```

## Пользовательские роли и права доступа
- ### Аноним
Может просматривать описания произведений, читать отзывы и комментарии.
- ### Аутентифицированный пользователь (user)
Может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
- ### Модератор (moderator)
Те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.
- ### Администратор (admin)
Полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
- ### Суперпользователь Django
Всегда обладает правами администратора, пользователя с правами admin. Даже если изменить пользовательскую роль суперпользователя — это не лишит его прав администратора. Суперпользователь — всегда администратор, но администратор — не обязательно суперпользователь.

## Самостоятельная регистрация новых пользователей
- Пользователь отправляет POST-запрос с параметрами email и username на эндпоинт /api/v1/auth/signup/.
- Сервис YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на указанный адрес email.
- Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).

В результате пользователь получает токен и может работать с API проекта, отправляя этот токен с каждым запросом.  
После регистрации и получения токена пользователь может отправить PATCH-запрос на эндпоинт /api/v1/users/me/ и заполнить поля в своём профайле (описание полей — в документации).

## Создание пользователя администратором
Пользователей создаёт администратор — через админ-зону сайта или через POST-запрос на специальный эндпоинт api/v1/users/ (описание полей запроса для этого случая есть в документации). При создании пользователя не предполагается автоматическая отправка письма пользователю с кодом подтверждения.  

После этого пользователь должен самостоятельно отправить свой email и username на эндпоинт /api/v1/auth/signup/ , в ответ ему должно прийти письмо с кодом подтверждения.  

Далее пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен), как и при самостоятельной регистрации.  

## Связанные данные и каскадное удаление
- При удалении объекта пользователя User удаляться все отзывы и комментарии этого пользователя (вместе с оценками-рейтингами).
- При удалении объекта произведения Title удаляться все отзывы к этому произведению и комментарии к ним.
- При удалении объекта отзыва Review будут удалены все комментарии к этому отзыву.
- При удалении объекта категории Category связанные с этой категорией произведения не будут удалены.
- При удалении объекта жанра Genre связанные с этим жанром произведения не будут удалены.

### Эндпоинты:
`api/v1/auth/signup/` - (POST): Передаём email и username, регистрируем пользователя.

`api/v1/auth/token/` - (POST): Передаём username и confirmation code, получаем JWT-токен.

`api/v1/categories/` - (GET, POST): Получаем список категорий. Либо создаём новую категорию, передавая name и slug (требуется токен).

`api/v1/categories/{slug}/` -  (DELETE): передаём slug, удаляем категорию (требуется токен).

`api/v1/genres/` - (GET, POST): Получаем список всех жанров. Либо создаём новый жанр, передавая name и slug (требуется токен).

`api/v1/genres/{slug}/` - (DELETE): передаём slug, удаляем жанр (требуется токен).

`api/v1/titles/` - (GET, POST): Получаем список всех объектов. Либо создаём новое произведение, передавая name, year, description, genre, category (требуется токен).

`api/v1/titles/{titles_id}/` - (GET, PATCH, DELETE): Получаем информацию о произведение, передавая titles_id. Либо частично обновляем, передвая titles_id и name, year, description, genre, category (требуется токен). Либо удаляем произведение, передвая titles_id (требуется токен).

`api/v1/titles/{title_id}/reviews/` - (GET, POST): Получаем список всех отзывов, передавая titles_id. Либо добавляем новый отзыв, передавая titles_id и text, score (требуется токен).

`api/v1/titles/{title_id}/reviews/{review_id}/` - (GET, PATCH, DELETE): Получаем отзыв, передавая title_id, review_id. Либо частично обновляем, передавая title_id, review_id и text, score (требуется токен). Либо удаляем отзыв, передавая title_id, review_id (требуется токен).

`api/v1/titles/{title_id}/reviews/{review_id}/comments/` - (GET, POST): Получам список все комментариев к отзыву, передавая title_id, review_id. Либо добовляем комментарий к отзыву, передавая title_id, review_id и text (требуется токен).

`api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` - (GET, PATCH, DELETE): Получаем комментарий к отзыву по id, передавая title_id, review_id, comment_id. Либо частично обновляем комментарий, передавая title_id, review_id, comment_id и text (требуется токен). Либо удаляем комментарий, передавая title_id, review_id, comment_id (требуется токен).

`api/v1/users/` - (GET, POST): Получаем список всех пользователей, либо добавляем нового, передавая username, email, first_name, last_name, bio, role (требуется токен).

`api/v1/users/{username}/` - (GET, PATCH, DELETE): Получаем пользователя, передавая его username (требуется токен). Либо частично обновляем пользователя, передавая username, email, first_name, last_name, bio, role (требуется токен). Либо удаляем пользователя, передавая username (требуется токен).

`api/v1/users/me/` - (GET, PATCH): Получаем свои данные пользователя, либо обновляем свои данные, передавая username, email, first_name, last_name, bio, role (требуется токен).

# Документация к API
После запуска сервера, по адресу .../redoc/ будет доступна полная документация для YamDB api.

## Примеры запросов и ответы:
Регистрация пользователя:
`POST .../api/v1/auth/signup/`
```
{
  "email": "string",
  "username": "string"
}
```
Пример ответа:
```
{
  "email": "string",
  "username": "string"
}
```

GET-запрос на получение списка категорий
`GET .../api/v1/categories/`

Пример ответа:
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "^-$"
    }
  ]
}
```

Частичное обновление комментария к отзыву:
`PATCH .../api/v1/titles/7/reviews/1/comments/2/`
```
{
  "text": "string"
}
```
Пример ответа:
```
{
  "id": 2,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}
```


# Работали над проектом:
- [bl00dimir](https://github.com/bl00dimir) titles, categories, genres and DB functional.
- [NRmously](https://github.com/NRmously) TeamLead, auth and users functional.
- [Wyjink](https://github.com/Wyjink) reviews, comments and rating functional.
