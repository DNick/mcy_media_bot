# MCY Media Bot

Telegram-бот, который накладывает логотип MCY на присланные фото и видео и
возвращает результат файлом (без потери качества). Поддерживает изображения
(в т.ч. HEIC) и видео (`mp4`, `mov`).

## Возможности

- Фото: логотип в правом нижнем углу + повышение чёткости и насыщенности.
- Видео: логотип + лёгкое шумоподавление (`hqdn3d`), звук сохраняется.
- Приём как «фотографией»/«видео», так и файлом-документом.
- Уведомление мейнтейнера в чат при необработанной ошибке.

## Стек

- Python 3.14, пакетный менеджер [uv](https://docs.astral.sh/uv/)
- [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/), Pillow, pillow-heif, ffmpeg-python
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — типизированный конфиг из env/`.env`
- Системный `ffmpeg` (ставится в образ)

## Переменные окружения

| Переменная           | Описание                                          |
|----------------------|---------------------------------------------------|
| `BOT_TOKEN`          | Токен бота от [@BotFather](https://t.me/BotFather)|
| `MAINTAINER_CHAT_ID` | ID чата для уведомлений об ошибках                |

Скопируйте `.env.example` в `.env` и заполните значения.

## Локальный запуск

Пакетный менеджер проекта — [uv](https://docs.astral.sh/uv/)
(`brew install uv`). Окружение и версии фиксируются в `uv.lock`.

```bash
uv sync                # создаёт .venv по uv.lock (вкл. dev-зависимости)
cp .env.example .env   # затем впишите реальные значения
uv run python main.py
```

> Для обработки видео нужен установленный в системе `ffmpeg`.

## Запуск в Docker

```bash
cp .env.example .env   # впишите значения; compose подхватит .env автоматически
docker compose up -d --build
```

## Деплой через Portainer

1. **Stacks → Add stack**, способ *Repository* (укажите этот git-репозиторий)
   или *Web editor* (вставьте содержимое `docker-compose.yaml`).
2. В разделе **Environment variables** задайте `BOT_TOKEN` и `MAINTAINER_CHAT_ID`
   (файл `.env` в репозиторий не коммитится).
3. **Deploy the stack**. Контейнер перезапускается автоматически
   (`restart: unless-stopped`).

## Разработка

Проверка стиля (ruff входит в dev-зависимости):

```bash
uv run ruff check .
uv run ruff format .
```

Обновление зависимостей: правьте `pyproject.toml`, затем `uv lock` и `uv sync`.
