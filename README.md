# Telegram-GigaChat Bot

Лёгкий способ запустить Telegram-бота на базе GigaChat с помощью Docker Compose.

## 1. Предварительные требования

| Что нужно | Где взять |
|-----------|-----------|
| **Docker & Docker Compose** | [Официальная инструкция по установке Docker](https://docs.docker.com/engine/install/) <!-- :contentReference[oaicite:6]{index=6} --> |
| **Аккаунт в Sber Developers** | [GigaChat API — документация](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/gigachat-api) <!-- :contentReference[oaicite:7]{index=7} --> |
| **Учётная запись Telegram** | [Руководство «From BotFather to Hello World»](https://botcreators.ru/blog/kak-sozdat-svoego-bota-v-botfather/) <!-- :contentReference[oaicite:8]{index=8} --> |

> **Совет:** Для Linux-пользователей есть отдельное пошаговое руководство по установке Docker Engine на Ubuntu. <!-- :contentReference[oaicite:9]{index=9} -->

## 2. Получаем ключ авторизации GigaChat

1. Зарегистрируйтесь или войдите в [личный кабинет Sber Developers](https://developers.sber.ru/studio/workspaces/).  
2. Создайте новый проект и добавьте в него **GigaChat API**.  
3. На вкладке *Ключи авторизации* нажмите **Получить новый ключ**.  
4. Скопируйте этот ключ

## 3. Создаём Telegram-бота

1. Откройте диалог с [@BotFather](https://t.me/BotFather) в Telegram.  
2. Выполните команду `/newbot` и следуйте инструкциям → получите `BOT_TOKEN`. <!-- :contentReference[oaicite:11]{index=11} -->  

## 4. Добавляем бота в группу

1. Перейдите в группу
2. Добавьте бота, также, как добавляете пользователя
3. Сделайте бота администратором

## 5. Конфигурация через `.env`

Создайте файл `.env` (в корне проекта) с таким содержимым:

```env
BOT_TOKEN=<токен бота>
GIGACHAT_CREDENTIALS=<base64-ключ авторизации>
```

## 6. Заполнение бота информацией

Перейдите в директорию `project/knowledge` и удалите файл `python.md`

Вместо этого файла создайте файлы с расширениями `.txt` и `.md` с нужными знаниями

Также, вы можете изменить ответ бота, если он не знает ответ в файле `project/settings.py`

## 7. Запуск с Docker Compose

Сборка образов (если требуется) и запуск в фоновом режиме
```bash
docker compose up -d --build
```
Команда создаст и запустит все сервисы, определённые в docker-compose.yml, и выведет логи в консоль. <!-- :contentReference[oaicite:13]{index=13} -->

Для остановки используйте 
```bash
docker compose down
```