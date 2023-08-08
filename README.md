# Foodgram, «Продуктовый помощник»
## Описание
Веб-приложение для публикации рецептов различных блюд.
Пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стек технологий
Python 3.9.13, Django 3.2.3, Django REST Framework 3.12.4, PostgreSQL, Docker.

## Документация к API
Чтобы открыть документацию локально, запустите сервер и перейдите по ссылке:
[http://127.0.0.1/api/docs/](http://127.0.0.1/api/docs/)

## Установка
Для запуска локально, создайте файл `.env` в директории `/infra/` с содержанием:
```
SECRET_KEY=любой_секретный_ключ_на_ваш_выбор
DEBUG=False
ALLOWED_HOSTS=*,или,ваши,хосты,через,запятые,без,пробелов

POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=пароль_к_базе_данных_на_ваш_выбор
DB_HOST=bd
DB_PORT=5432
```

#### Установка Docker
Для запуска проекта вам потребуется установить Docker и docker-compose.

Для установки на ubuntu выполните следующие команды:
```bash
sudo apt install docker docker-compose
```

### Настройка проекта
1. Запустите docker compose:
```bash
docker compose up -d
```
2. Примените миграции:
```bash
docker compose exec backend python manage.py migrate
```
3. Заполните базу начальными данными (необязательно):
```bash
docker compose exec backend python manange.py load_data
```
4. Создайте администратора:
```bash
docker compose exec backend python manage.py createsuperuser
```
5. Соберите статику:
```bash
docker compose exec backend python manage.py collectstatic
```
