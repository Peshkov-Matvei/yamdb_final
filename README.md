![example workflow](https://github.com/github/yamdb_final/.github/workflows/yamdb_workflow/badge.svg)
![Build Status](https://github.com/Peshk-Matvei/yamdb_final/workflows/Run%20tests/badge.svg)](https://github.com/Peshk-Matvei/yamdb_final/actions/workflows/yamdb_workflow.yml)
# Проект yamdb_final
### Описание
API проект для получения информации, выполненное в ходе подготовки к командной работе.
### Технологии
- Python
- Django
- Docker
- docker-compose
### Шаблон env-файла
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
### Команды для запуска приложения
- Склонируйте репозитрий 
```
git clone https://github.com/Peshkov-Matvei/yamdb_final.git
```
- Войдите в папку infra/
- соберите образ docker-compoce
```
docker-compose up -d --build
```
- Запустите миграции
```
docker-compose exec web python manage.py migrate
```
- Запустите статику
```
docker-compose exec web python manage.py collectstatic --no-input
```
- Создайте суперюзера
```
docker-compose exec web python manage.py createsuperuser
```
- Заполните базу данных 
```
docker-compose exec web python manage.py loaddata fixtures.json
```
### Автор проекта
Пешков Матвей студент ЯндексПрактикума
### Развернутый проект можно посмотреть по ссылке:
http://51.250.15.12
