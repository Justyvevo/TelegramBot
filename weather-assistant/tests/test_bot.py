import asyncio
import unittest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.exceptions import TelegramForbiddenError
from aiogram.methods import SendMessage
from aiogram.types import Chat, Message, Update, User

from weather_assistant.__main__ import run
from weather_assistant.bot import HELP, Assistant, create_dispatcher
from weather_assistant.config import Settings
from weather_assistant.demo import sample_payload
from weather_assistant.notifications import StopNotifications
from weather_assistant.weather import Weather, WeatherClient, WeatherError


class SettingsTests(unittest.TestCase):
    def test_defaults_and_secret_repr(self):
        settings = Settings.from_env(
            {"TELEGRAM_BOT_TOKEN": "fake-token", "WEATHER_API_KEY": "fake-key"}
        )
        self.assertEqual(settings.notification_interval, 14400)
        self.assertNotIn("fake", repr(settings))

    def test_missing_credentials(self):
        for values in ({}, {"TELEGRAM_BOT_TOKEN": "fake"}, {"WEATHER_API_KEY": "fake"}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                Settings.from_env(values)

    def test_invalid_intervals(self):
        for interval in ("abc", "0", "59", "604801", "1.5"):
            values = {
                "TELEGRAM_BOT_TOKEN": "fake",
                "WEATHER_API_KEY": "fake",
                "NOTIFICATION_INTERVAL_SECONDS": interval,
            }
            with self.subTest(interval=interval), self.assertRaises(ValueError):
                Settings.from_env(values)

    def test_valid_interval_boundaries(self):
        for interval in ("60", "604800"):
            values = {
                "TELEGRAM_BOT_TOKEN": "fake",
                "WEATHER_API_KEY": "fake",
                "NOTIFICATION_INTERVAL_SECONDS": interval,
            }
            self.assertEqual(Settings.from_env(values).notification_interval, int(interval))


class AssistantTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=Bot)
        self.weather = AsyncMock(spec=WeatherClient)
        self.weather.get.return_value = Weather.from_payload(sample_payload())
        self.assistant = Assistant(self.bot, self.weather, 14400)

    async def asyncTearDown(self):
        await self.assistant.close()

    async def test_help_does_not_query_weather(self):
        self.assertEqual(await self.assistant.handle(1, "/help"), HELP)
        self.weather.get.assert_not_awaited()

    async def test_city_selection_and_refresh(self):
        reply = await self.assistant.handle(1, "/weather Waterford, Ireland")
        self.assertIn("Waterford", reply)
        self.assertEqual(self.assistant.states[1].city, "Waterford, Ireland")
        await self.assistant.handle(1, "/weather")
        self.weather.get.assert_awaited_with("Waterford, Ireland")

    async def test_plain_text_city(self):
        await self.assistant.handle(1, "Dublin")
        self.weather.get.assert_awaited_once_with("Dublin")

    async def test_notify_requires_city(self):
        self.assertIn("Choose a city", await self.assistant.handle(1, "/notify"))
        self.assertFalse(self.assistant.notifications._tasks)

    async def test_refresh_requires_city(self):
        self.assertIn("Choose a city", await self.assistant.handle(1, "/weather"))

    async def test_duplicate_notify_and_stop(self):
        await self.assistant.handle(1, "Waterford")
        self.assertIn("every 240 minutes", await self.assistant.handle(1, "/notify"))
        self.assertIn("already on", await self.assistant.handle(1, "/notify"))
        await self.assistant.handle(1, "/stop")
        self.assertFalse(self.assistant.notifications._tasks)

    async def test_failed_lookup_preserves_previous_city(self):
        await self.assistant.handle(1, "Waterford")
        self.weather.get.side_effect = WeatherError("City not found")
        self.assertEqual(await self.assistant.handle(1, "BadCity"), "City not found")
        self.assertEqual(self.assistant.states[1].city, "Waterford")

    async def test_unknown_command_does_not_call_api(self):
        self.assertIn("Unknown command", await self.assistant.handle(1, "/unknown"))
        self.weather.get.assert_not_awaited()

    async def test_forget_clears_preferences_and_subscription(self):
        await self.assistant.handle(1, "Waterford")
        await self.assistant.handle(1, "/notify")
        await self.assistant.handle(1, "/forget")
        self.assertNotIn(1, self.assistant.states)
        self.assertFalse(self.assistant.notifications._tasks)

    async def test_chat_state_is_isolated(self):
        await self.assistant.handle(1, "Waterford")
        await self.assistant.handle(2, "Dublin")
        self.assertEqual(self.assistant.states[1].city, "Waterford")
        self.assertEqual(self.assistant.states[2].city, "Dublin")

    async def test_chat_limit_is_bounded(self):
        self.assistant.max_chats = 1
        await self.assistant.handle(1, "Waterford")
        self.assertIn("session limit", await self.assistant.handle(2, "Dublin"))
        self.assertEqual(len(self.assistant.states), 1)

    async def test_notification_fetches_once(self):
        await self.assistant.handle(1, "Waterford")
        self.weather.get.reset_mock()
        await self.assistant._notify(1)
        self.weather.get.assert_awaited_once_with("Waterford")
        self.bot.send_message.assert_awaited_once()

    async def test_blocked_bot_is_terminal(self):
        await self.assistant.handle(1, "Waterford")
        self.bot.send_message.side_effect = TelegramForbiddenError(
            method=SendMessage(chat_id=1, text="test"), message="blocked"
        )
        with self.assertRaises(StopNotifications):
            await self.assistant._notify(1)

    async def test_commands_for_same_chat_are_serialized(self):
        entered, release = asyncio.Event(), asyncio.Event()

        async def lookup(city):
            if city == "Waterford":
                entered.set()
                await release.wait()
            return Weather.from_payload(sample_payload())

        self.weather.get.side_effect = lookup
        first = asyncio.create_task(self.assistant.handle(1, "Waterford"))
        await asyncio.wait_for(entered.wait(), 1)
        second = asyncio.create_task(self.assistant.handle(1, "Dublin"))
        release.set()
        await asyncio.wait_for(asyncio.gather(first, second), 1)
        self.assertEqual(self.assistant.states[1].city, "Dublin")


class FakeSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.sent = []
        self.closed = False

    async def close(self):
        self.closed = True

    async def make_request(self, bot, method, timeout=None):
        if not isinstance(method, SendMessage):
            raise AssertionError(f"Unexpected method: {type(method).__name__}")
        self.sent.append(method)
        return Message(
            message_id=100,
            date=datetime.now(UTC),
            chat=Chat(id=int(method.chat_id), type="private"),
            text=method.text,
        )

    async def stream_content(
        self, url, headers=None, timeout=30, chunk_size=65536, raise_for_status=True
    ):
        raise AssertionError("No downloads allowed in offline tests")
        yield b""  # Makes this the async iterator required by BaseSession.


class DispatcherIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = FakeSession()
        self.bot = Bot("123456:OFFLINE_TEST_TOKEN_NOT_A_REAL_CREDENTIAL", session=self.session)
        self.weather = AsyncMock(spec=WeatherClient)
        self.weather.get.return_value = Weather.from_payload(sample_payload())
        self.assistant = Assistant(self.bot, self.weather, 14400)
        self.dp = create_dispatcher(self.assistant)

    async def asyncTearDown(self):
        await self.assistant.close()
        await self.bot.session.close()
        await self.dp.storage.close()

    async def feed(self, text=None, chat_type="private"):
        message = Message(
            message_id=1,
            date=datetime.now(UTC),
            chat=Chat(id=1, type=chat_type),
            from_user=User(id=1, is_bot=False, first_name="Test"),
            text=text,
        )
        await self.dp.feed_update(self.bot, Update(update_id=1, message=message))

    async def test_private_message_round_trip(self):
        await self.feed("/weather Waterford, Ireland")
        self.assertEqual(len(self.session.sent), 1)
        self.assertIn("1012 hPa", self.session.sent[0].text)
        self.weather.get.assert_awaited_once_with("Waterford, Ireland")

    async def test_non_text_message_prompts_for_city(self):
        await self.feed()
        self.assertIn("as text", self.session.sent[0].text)
        self.weather.get.assert_not_awaited()

    async def test_group_message_is_ignored(self):
        await self.feed("Waterford", chat_type="group")
        self.assertEqual(self.session.sent, [])
        self.weather.get.assert_not_awaited()

    async def test_application_startup_and_shutdown_without_network(self):
        dispatcher = AsyncMock()
        with (
            patch("weather_assistant.__main__.Bot", return_value=self.bot),
            patch("weather_assistant.__main__.create_dispatcher", return_value=dispatcher),
        ):
            await run(Settings("fixture-token", "fixture-key"))
        dispatcher.start_polling.assert_awaited_once_with(self.bot, close_bot_session=False)
        self.assertTrue(self.session.closed)

    async def test_application_closes_session_when_polling_fails(self):
        dispatcher = AsyncMock()
        dispatcher.start_polling.side_effect = RuntimeError("simulated polling failure")
        with (
            patch("weather_assistant.__main__.Bot", return_value=self.bot),
            patch("weather_assistant.__main__.create_dispatcher", return_value=dispatcher),
            self.assertRaisesRegex(RuntimeError, "simulated polling failure"),
        ):
            await run(Settings("fixture-token", "fixture-key"))
        self.assertTrue(self.session.closed)
