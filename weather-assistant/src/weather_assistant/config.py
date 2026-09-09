"""Configuration validation without exposing secrets in errors or repr output."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    telegram_token: str = field(repr=False)
    weather_api_key: str = field(repr=False)
    notification_interval: int = 14400

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if env is None else env
        token = values.get("TELEGRAM_BOT_TOKEN", "").strip()
        key = values.get("WEATHER_API_KEY", "").strip()
        if not token or not key:
            raise ValueError(
                "Set TELEGRAM_BOT_TOKEN and WEATHER_API_KEY in your environment or .env."
            )
        try:
            interval = int(values.get("NOTIFICATION_INTERVAL_SECONDS", "14400"))
        except ValueError:
            raise ValueError("NOTIFICATION_INTERVAL_SECONDS must be an integer.") from None
        if not 60 <= interval <= 604800:
            raise ValueError("NOTIFICATION_INTERVAL_SECONDS must be between 60 and 604800.")
        return cls(token, key, interval)
