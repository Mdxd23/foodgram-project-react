# Foodgram


## Админка
Логин:
```
admin
```
E-mail:
```
admin@admin.admin
```
Пароль:
```
admin
```

## Описание проекта

Сайт с возможностью создания, редактирования рецептов!

## Технологии

- Python 3.9
- Django
- Gunicorn
- Nginx
- Certbot
- Docker
- GitHub Actions

### Запуск проекта
1. Скопировать репо:
```
git clone git@github.com:Mdxd23/foodgram-project-react.git
```
2. В папке /backend создать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```
3. В корне проекта создать файл .env и добавить в него свои данные по примеру данных из .env.example
4. Запустить проект через docker-compose:
```
docker compose -f docker-compose.yml up
```
5. Выполнить миграции:
```
docker compose -f docker-compose.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.yml exec backend python manage.py migrate
```