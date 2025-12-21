# infrastructure/storage/base_adapter.py
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Optional, Dict

class CacheAdapter(ABC):
    @abstractmethod
    async def read_day(self, day: date) -> Optional[Dict[Any, Any]]:
        pass

    @abstractmethod
    async def write_day(self, day: date, data: Dict[Any, Any]) -> None:
        pass

    @abstractmethod
    async def get_last_update_time(self, day: date) -> Optional[datetime]:
        pass

    @abstractmethod
    async def cleanup_old(self) -> None:
        pass