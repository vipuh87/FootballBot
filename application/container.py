# application/container.py
from aiogram import Bot

from application.api.api_client import ApiClient
from application.services.cache_service import CacheService
from application.services.match_repository import MatchRepository
from application.services.rate_limiter import RateLimiterService
from application.services.push_service import PushService
from application.services.update_scheduler import UpdateScheduler
from application.services.news_digest_service import NewsDigestService
from application.services.match_details_service import MatchDetailsService
from application.services.ukrainian_player_performance_service import UkrainianPlayerPerformanceService
from config import USE_REDIS, REDIS_URL

class Container:
    _instance = None

    def __init__(self, bot: Bot):
        self.bot = bot
        self.api = ApiClient()

        if USE_REDIS:
            import redis.asyncio as redis
            from infrastructure.storage.redis_adapter import RedisCacheAdapter
            redis_client = redis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            adapter = RedisCacheAdapter(redis_client)
        else:
            from infrastructure.storage.json_adapter import JsonCacheAdapter
            adapter = JsonCacheAdapter()

        self.cache = CacheService(adapter)
        self.repo = MatchRepository(self.cache)
        self.limiter = RateLimiterService(self.api)
        self.push = PushService(bot, self.repo)
        self.player_performance = UkrainianPlayerPerformanceService()  # спочатку
        self.digest = NewsDigestService(self.repo, self.player_performance)  # потім передаємо
        self.match_details = MatchDetailsService(self.repo, self.api)
        self.update_scheduler = UpdateScheduler(
            api=self.api, cache=self.cache, limiter=self.limiter, push=self.push, bot=bot, repo=self.repo
        )

    @classmethod
    def init(cls, bot: Bot):
        if cls._instance is not None:
            raise RuntimeError("Container вже ініціалізовано")
        cls._instance = cls(bot)

    @classmethod
    def get(cls):
        if cls._instance is None:
            raise RuntimeError("Container не ініціалізовано!")
        return cls._instance