# Футбольний Telegram бот

Модульна архітектура на Python з aiogram 3.x.
Фічі: дайджест новин за вчора, матчі (Вчора/Сьогодні/Завтра), команди, гравці, нагадування за 15 хв, ручне оновлення з лімітом, кеш на Redis.
Автоматичний ранковий дайджест з клавіатурою.

## Деплой без ноутбука

Рекомендована безкоштовна схема:

- Vercel: приймає Telegram webhook і HTTP-запит `/api/cron`.
- GitHub Actions: кожні 5 хвилин викликає `/api/cron`.
- Redis на free-tier, наприклад Upstash: зберігає кеш матчів і стан надісланих нагадувань.

### Environment variables на Vercel

Обов'язкові:

- `BOT_TOKEN`
- `API_SPORTS_KEY`
- `PUBLIC_BASE_URL`, наприклад `https://your-project.vercel.app`
- `WEBHOOK_SECRET`, випадковий рядок з букв/цифр/`_`/`-`
- `CRON_SECRET`, випадковий довгий рядок
- `USE_REDIS=true`
- `REDIS_URL`

Опційні:

- `YOUTUBE_API_KEY`
- `GROUP_CHAT_ID`
- `GROUP_TOPIC_ID`
- `CACHE_RETENTION_DAYS`

### GitHub Actions secrets

У репозиторії GitHub додай:

- `PUBLIC_BASE_URL`
- `CRON_SECRET`

Workflow `.github/workflows/cron.yml` буде викликати `GET /api/cron` кожні 5 хвилин.

### Встановити Telegram webhook

Після деплою на Vercel локально виконай:

```bash
python scripts/set_webhook.py
```

Поки webhook увімкнений, polling через `python bot.py` для цього самого бота не треба запускати.
