## Данное приложение представляет из себя сервис по обработке платежей. Поступающие транзакции обрабатываются и зачисляются на баланс пользователя. 

<details>
<summary>Стек</summary>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

</details>
<details>
<summary>Автор</summary>

[avdeevdmitrykrsk](https://github.com/avdeevdmitrykrsk)
</details>

## Для развертывания проекта необходимо:
1. Склонировать репозиторий
```sh
git clone git@github.com:avdeevdmitrykrsk/payment_service.git
```
2. Перейти в папку `src`
```sh
cd src
```
3. Установить зависимости
```sh
pip install -r requirements.txt
```
4. Настроить файл конфигураций по примеру файла `.env.example`
5. Применить миграции `alembic`
```sh
alembic upgrade head
```
6. Аутентифицироваться по адресу `/api/auth/register/`
```json
{
    "email": "<email>",
    "password": "<password>"
}
```
7. Получить токен аутентификации по адресу `/api/auth/jwt/login/`
```json
{
    "username": "<email>",
    "password": "<password>"
}
```
### При дальнейших запросах указывать токен в заголовках (Bearer)

## При запуске приложения будут автоматически созданы:
1. Пользователь с правами `user`
2. Аккаунт пользователя
3. Пользователь с правами `superuser`
## Для этого необходимо в .env файле указать `email` и `password` - на основе этих данных будут созданы пользователи.


## Проект можно запустить в 2-ух режимах:
1. В `debug` режиме: для этого необходимо в файле конфигураций установить `DEBUG=True`, в данном случае проект запустится локально на БД `sqlite` и `uvicorn`. Для этого из папки `src` выполнить команду:
```sh
uvicorm main:app --reload
```
1. В `production` режиме: для этого необходимо в файле конфигураций установить `DEBUG=False`, в данном случае проект запустится в `docker-compose`-контейнерах на БД `postgres`. Для этого из корневой папки приложения выполнить команду (миграции `alembic` применятся автоматически):
```sh
docker-compose up
```
