# infrastructure/storage/json_adapter.py
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from datetime import date

from config import CACHE_RETENTION_DAYS

DATA_DIR = Path("data/matches")
DATA_DIR.mkdir(exist_ok=True, parents=True)

from .base_adapter import CacheAdapter

class JsonCacheAdapter(CacheAdapter):
    def _file(self, day: date) -> Path:
        return DATA_DIR / f"{day.isoformat()}.json"

    async def read_day(self, day: date) -> Optional[Dict[Any, Any]]:
        file = self._file(day)
        if not file.exists():
            return None
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    async def write_day(self, day: date, data: Dict[Any, Any]) -> None:
        file = self._file(day)
        tmp = file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(file)

    async def get_last_update_time(self, day: date) -> Optional[datetime]:
        file = self._file(day)
        if not file.exists():
            return None
        return datetime.fromtimestamp(file.stat().st_mtime)

    async def cleanup_old(self) -> None:
        limit = datetime.now() - timedelta(days=CACHE_RETENTION_DAYS)
        for file in DATA_DIR.glob("*.json"):
            try:
                day = datetime.fromisoformat(file.stem)
                if day.date() < limit.date():
                    file.unlink()
            except Exception:
                pass