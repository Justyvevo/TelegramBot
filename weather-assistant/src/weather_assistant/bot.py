"""Telegram UI adapter. Weather parsing and guidance live outside the handlers."""

import asyncio
from dataclasses import dataclass, field

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message

from weather_assistant.notifications import NotificationManager, StopNotifications
from weather_assistant.weather import WeatherClient, WeatherError, format_weather

HELP = (
    "Weather Assistant\n\n"
    "Send a city, e.g. Waterford, Ireland, or use /weather <city>.\n"
    "/weather - refresh your selected city\n"
    "/notify - opt in to periodic weather messages\n"
    "/stop - stop notifications\n"
    "/forget - stop notifications and clear your selected city\n"
    "/help - show these commands\n\n"
    "Preferences are held in memory and reset when the bot restarts. "
    "City queries are sent to WeatherAPI; no precise location is required."
)


@dataclass
class ChatState:
    city: str | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class Assistant:
    def __init__(self, bot: Bot, weather: WeatherClient, interval: int, max_chats: int = 1000):
        self.bot, self.weather, self.interval, self.max_chats = bot, weather, interval, max_chats
        self.states: dict[int, ChatState] = {}
        self.notifications = NotificationManager(self._notify, interval)

    async def _notify(self, chat_id: int) -> None:
        state = self.states.get(chat_id)
        if state is None or state.city is None:
            raise StopNotifications
        city = state.city
        weather = await self.weather.get(city)
        # Do not send an old forecast if the city was changed during the request.
        if self.states.get(chat_id) is not state or state.city != city:
            return
        try:
            await self.bot.send_message(chat_id, format_weather(weather))
        except TelegramForbiddenError:
            raise StopNotifications from None

    async def handle(self, chat_id: int, text: str) -> str:
        stripped = text.strip()
        if stripped.split(maxsplit=1)[0:1] in (["/help"], ["/start"]):
            return HELP
        state = self.states.get(chat_id)
        if state is None:
            if len(self.states) >= self.max_chats:
                return "This demo has reached its session limit. Please try again later."
            state = self.states[chat_id] = ChatState()
        async with state.lock:
            # /forget can have removed a state while another handler waited for its lock.
            if self.states.get(chat_id) is not state:
                return "Your previous session was cleared. Please send your command again."
            if stripped == "/forget":
                await self.notifications.stop(chat_id)
                self.states.pop(chat_id, None)
                return "Notifications stopped and your selected city cleared."
            if stripped == "/stop":
                await self.notifications.stop(chat_id)
                return "Notifications are off."
            if stripped == "/notify":
                if state.city is None:
                    return "Choose a city first, e.g. /weather Waterford, Ireland."
                if not self.notifications.start(chat_id):
                    return "Notifications are already on. Use /stop to turn them off."
                return (
                    f"Notifications on: every {self.interval // 60} minutes for {state.city}. "
                    "The first message will arrive after that interval. Use /stop to opt out."
                )
            command, _, argument = stripped.partition(" ")
            if command == "/weather":
                city = argument.strip() or state.city
                if city is None:
                    return "Choose a city first, e.g. /weather Waterford, Ireland."
            elif stripped.startswith("/"):
                return "Unknown command. Use /help to see available commands."
            else:
                city = stripped
            try:
                result = await self.weather.get(city)
            except WeatherError as exc:
                return str(exc)
            state.city = city
            return format_weather(result)

    async def close(self) -> None:
        await self.notifications.close()
        self.states.clear()


def create_dispatcher(assistant: Assistant) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(F.chat.type == ChatType.PRIVATE, F.text)
    async def message_handler(message: Message) -> None:
        reply = await assistant.handle(message.chat.id, message.text or "")
        await message.answer(reply)

    @dp.message()
    async def unsupported(message: Message) -> None:
        if message.chat.type == ChatType.PRIVATE:
            await message.answer("Please send a city as text, or use /help.")
        # Ignore groups: there is deliberately no shared group-city state.

    return dp
