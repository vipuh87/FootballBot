# application/services/video_service.py
# application/services/video_service.py
import httpx
from datetime import datetime, timezone, timedelta
from config import YOUTUBE_API_KEY
from data.selected_teams import TEAMS

async def search_match_highlight(match) -> str | None:
    """Пріоритет: канали клубів > транслятори > загальний пошук"""
    # Кеш: якщо вже є посилання — повертаємо його
    if match.video_url:
        print(f"Відео з кешу для матчу {match.fixture_id}: {match.video_url}")
        return match.video_url

    query = f"{match.home} {match.away}"

    published_after_dt = datetime.now(timezone.utc) - timedelta(days=3)
    published_after = published_after_dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Канали клубів (з selected_teams)
    club_channels = []
    home_data = TEAMS.get(match.home_id)
    away_data = TEAMS.get(match.away_id)
    if home_data and home_data.get("youtube_channel_id"):
        club_channels.append(home_data["youtube_channel_id"])
    if away_data and away_data.get("youtube_channel_id"):
        club_channels.append(away_data["youtube_channel_id"])

    # 2. Транслятори (Megogo, Setanta, Sky)
    broadcaster_channels = [
        "UCAvNr5DMVncoJnJAotXOjOQ",  # Megogo
        "UC-M4dS7_cd-k5ZGr-8rHi0g",  # Setanta
        "UCAvNr5DMVncoJnJAotXOjOQ",  # Sky Sports
    ]

    # Усі пріоритетні канали
    priority_channels = club_channels + broadcaster_channels

    async def youtube_search(channel_id: str | None = None) -> str | None:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 5,
            "order": "date",
            "publishedAfter": published_after,
            "key": YOUTUBE_API_KEY,
        }
        if channel_id:
            params["channelId"] = channel_id

        try:
            # Ключовий фікс: правильний URL + follow_redirects
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

            if data.get("items"):
                video_id = data["items"][0]["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"Знайдено відео на каналі {channel_id or 'загальний'}: {video_url}")

                # Зберігаємо в кеш матчу
                match.video_url = video_url
                from application.container import Container
                await Container.get().repo.save_match(match)

                return video_url

            print(f"Немає відео на каналі {channel_id or 'загальний'} для {match.home} — {match.away}")
        except Exception as e:
            print(f"YouTube помилка на каналі {channel_id or 'загальний'}: {e}")

        return None

    # Поетапний пошук
    for channel_id in priority_channels:
        video_url = await youtube_search(channel_id)
        if video_url:
            return video_url

    # Загальний пошук як fallback
    return await youtube_search()
