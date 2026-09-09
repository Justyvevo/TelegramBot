"""Run with `python -m weather_assistant` after configuring a local .env."""

import asyncio
import logging

import httpx
from aiogram import Bot
from dotenv import load_dotenv

from weather_assistant.bot import Assistant, create_dispatcher
from weather_assistant.config import Settings
from weather_assistant.weather import WeatherClient


async def run(settings: Settings) -> None:
    async with httpx.AsyncClient() as http, Bot(settings.telegram_token) as bot:
        assistant = Assistant(
            bot, WeatherClient(http, settings.weather_api_key), settings.notification_interval
        )
        try:
            await create_dispatcher(assistant).start_polling(bot, close_bot_session=False)
        finally:
            await assistant.close()


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    # Request URLs can contain the WeatherAPI key. Never enable HTTP debug logs in production.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    try:
        settings = Settings.from_env()
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    try:
        asyncio.run(run(settings))
    except KeyboardInterrupt:
        pass
    except Exception:
        # SDK errors may carry request data; keep terminal output free of credentials.
        raise SystemExit(
            "Bot stopped. Check credentials, connectivity "
            "and that no other bot instance is polling."
        ) from None


if __name__ == "__main__":
    main()
