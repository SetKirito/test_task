# Backend API для лендинг-презентации разработчика

Этот проект представляет собой backend-сервис на FastAPI для лендинг-страницы разработчика. Он принимает заявки с формы обратной связи, сохраняет их в PostgreSQL, проводит AI-анализ комментария, логирует запросы и ошибки, а также отправляет email-уведомления.

![Swagger](/swagger.png)

Пример работы Swagger проекта

## 1. Как запустить проект

### Требования

- Docker и Docker Compose
- Python 3.11 (если запускать без Docker)
- Git

### 1. Клонирование репозитория

```bash
git clone https://github.com/SetKirito/Backend-API.git
cd test_task
```

### 2. Создание файла окружения

Создайте файл `.env` в корне проекта и заполните его следующими переменными:

```env
DATABASE_URL=postgresql://backend:backend@db:5432/backend
POSTGRES_DB=backend
POSTGRES_USER=backend
POSTGRES_PASSWORD=backend

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_SSL=false
OWNER_EMAIL=your_email@gmail.com
```

### 3. Запуск через Docker

```bash
docker compose up -d --build
```

### 4. Проверка работы

API будет доступно по адресам:

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health
- Metrics: http://127.0.0.1:8000/api/metrics

### Запуск локально без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 2. Стек технологий

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Docker Compose

### AI

- OpenAI API

### Дополнительно

- Logging в файлы
- Middleware для CORS и rate limiting
- Global exception handlers

## 3. Архитектура

Проект реализован по слоистой архитектуре:

```text
Router / API layer
    ↓
Controller layer
    ↓
Service layer
    ↓
Repository layer
    ↓
Database / external services
```

### Структура проекта

```text
app/
  api/            # маршруты и эндпоинты
  controllers/    # контроллеры
  services/       # бизнес-логика
  repositories/   # работа с БД
  models/         # SQLAlchemy модели
  core/           # конфигурация, middleware, logging, БД
  schemas/        # Pydantic схемы
```

### Паттерны и подходы

- Layered architecture
- Dependency injection через FastAPI `Depends`
- Separation of concerns: отдельные сервисы для AI, SMTP, логирования и базы данных
- Graceful fallback для внешних сервисов

## 4. Реализация API

### Эндпоинты

#### POST /api/contact

Создаёт заявку обратной связи.

Тело запроса:

```json
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+79990001122",
  "comment": "Здравствуйте, хочу уточнить условия"
}
```

Пример запроса:

```bash
curl -X POST http://127.0.0.1:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "phone": "+79990001122",
    "comment": "Здравствуйте, хочу уточнить условия"
  }'
```

Успешный ответ:

```json
{
  "success": true,
  "id": 1,
  "ai": {
    "sentiment": "neutral",
    "category": "Other"
  }
}
```

#### GET /api/health

Проверка состояния сервиса.

```bash
curl http://127.0.0.1:8000/api/health
```

Пример ответа:

```json
{
  "status": "ok",
  "database": "connected",
  "ai": "available"
}
```

#### GET /api/metrics

Возвращает статистику по заявкам.

```bash
curl http://127.0.0.1:8000/api/metrics
```

Пример ответа:

```json
{
  "total_contacts": 4,
  "today": 4,
  "positive": 0,
  "negative": 0
}
```

### Валидация и обработка ошибок

- Входные данные валидируются через Pydantic.
- Ошибки валидации возвращают `422`.
- Ошибки бизнес-логики и непредвиденные исключения обрабатываются глобальным exception handler.
- Rate limiting возвращает `429 Too Many Requests`.

## 5. AI-интеграция

### Что используется

- OpenAI API
- Используется для анализа комментария пользователя

### Для чего

- Определение тональности: positive / neutral / negative
- Классификация типа обращения: Question / Feedback / Commercial / Bug / Other

### Fallback

Если AI недоступен или API-ключ не задан:

- сервис не падает, заявка всё равно сохраняется в БД, возвращается безопасный fallback:

```json
{
  "sentiment": "unknown",
  "category": "Other"
}
```


## 6. Что сделано с помощью AI

Часть проекта была реализована с помощью AI-помощи в следующих аспектах:

- помощь с интеграцией OpenAI;
- формирование middleware, logging и exception handlers;

## 7. Хранение данных

### База данных

- Используется PostgreSQL
- Заявки сохраняются в таблицу `contacts`

### Логи

- Все HTTP-запросы логируются в файл `logs/app.log`
- Ошибки логируются в `logs/errors.log`

### Rate limiting

- Реализован простой middleware rate limiting по IP
- При превышении лимита возвращается `429`

### Статистика

- Метрики строятся прямо из базы данных по количеству заявок, количеству заявок за сегодня и количеству положительных/отрицательных AI-результатов

## 8. Примечания

Проект рассчитан на демонстрацию backend-архитектуры и взаимодействия с AI-интеграциями. Он показывает полный цикл:

1. Получение запроса
2. Валидация данных
3. Сохранение в БД
4. AI-анализ
5. Отправка email-уведомлений
6. Возврат ответа клиенту
