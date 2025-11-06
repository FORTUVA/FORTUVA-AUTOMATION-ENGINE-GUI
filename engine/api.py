import os
from typing import Any, Dict, List, Optional

import requests


API_URL = os.getenv("API_URL", "https://botapi.fortuva.xyz")


class FortuvaApi:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10_000) -> None:
        self.base_url = base_url or API_URL
        self.timeout = timeout / 1000.0  # requests takes seconds

    def _get(self, path: str) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}{path}"
        return requests.get(url, timeout=self.timeout)

    def get_failed_bet_count(self, wallet: str, round_number: int, start_round: int) -> int:
        try:
            resp = self._get(f"/user/failed-bet-count/{wallet}?roundNumber={round_number}&startRound={start_round}")
            resp.raise_for_status()
            return int(resp.json())
        except Exception:
            return 0

    def get_claimable_bets(self, wallet: str) -> List[Dict[str, Any]]:
        try:
            resp = self._get(f"/user/claimable-bet/{wallet}")
            resp.raise_for_status()
            data = resp.json()
            return list(data.get("data", []))
        except Exception:
            return []

    def get_cancelable_bets(self, wallet: str) -> List[Dict[str, Any]]:
        try:
            resp = self._get(f"/user/cancelable-bets/{wallet}")
            resp.raise_for_status()
            data = resp.json()
            return list(data.get("data", []))
        except Exception:
            return []

    def get_closeable_bets(self, wallet: str) -> List[Dict[str, Any]]:
        try:
            resp = self._get(f"/user/closeable-bets/{wallet}")
            resp.raise_for_status()
            data = resp.json()
            return list(data.get("data", []))
        except Exception:
            return []

    def get_round_info(self, round_number: int) -> Optional[Dict[str, Any]]:
        try:
            resp = self._get(f"/round/{round_number}")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return None
    
    def get_user_bets(self, wallet: str) -> List[Dict[str, Any]]:
        try:
            resp = self._get(f"/user/bets/{wallet}")
            resp.raise_for_status()
            data = resp.json()
            # Response has format: {"total": N, "data": [...]}
            if isinstance(data, dict) and 'data' in data:
                return list(data.get('data', []))
            return []
        except Exception:
            return []


# Singleton instance
fortuva_api = FortuvaApi()


