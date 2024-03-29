# Сервис Yatube
![yatube](https://github.com/1kovalevskiy/yatube/actions/workflows/main.yml/badge.svg)
![coverage](https://github.com/1kovalevskiy/yatube/blob/master/coverage.svg)

## Учебный сервис "Yatube" Личные блоги
Сервис микроблогов, на котором можно создать свою страницу, вести свой блог, читать посты других пользователей, подписываться на интересующих авторов и комментировать их посты.

Автор может выбрать имя и уникальный адрес для своей страницы.
Есть возможность модерировать записи и блокировать пользователей, если начнут присылать спам.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.

## Deploy
В корневой папке 
- Создать файл `.env` по примеру файла `.env.sample`
- Запустить `docker-compose up -d`

## Тестовый сервер
[Тестовый сервер ](http://yatube.kovalevskiy.xyz)http://yatube.kovalevskiy.xyz

## Технологии
- Приложение на Django
- Тестирование на "Pytest"
- БД PostgreSQL
- Proxy Nginx
- Контейнеризация с помощью Docker
