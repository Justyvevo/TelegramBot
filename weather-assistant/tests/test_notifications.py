import asyncio
import unittest
from unittest.mock import AsyncMock

from weather_assistant.notifications import NotificationManager, StopNotifications


class ControlledSleep:
    def __init__(self):
        self.requests = asyncio.Queue()

    async def __call__(self, interval):
        future = asyncio.get_running_loop().create_future()
        await self.requests.put((interval, future))
        await future

    async def tick(self):
        interval, future = await asyncio.wait_for(self.requests.get(), 1)
        future.set_result(None)
        return interval


class NotificationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.sleep = ControlledSleep()
        self.send = AsyncMock()
        self.manager = NotificationManager(self.send, 14400, sleep=self.sleep)

    async def asyncTearDown(self):
        await self.manager.close()

    async def test_duplicate_start_does_not_duplicate_task(self):
        self.assertTrue(self.manager.start(1))
        task = self.manager._tasks[1]
        self.assertFalse(self.manager.start(1))
        self.assertIs(self.manager._tasks[1], task)

    async def test_sends_after_interval_not_immediately(self):
        self.manager.start(1)
        self.send.assert_not_awaited()
        self.assertEqual(await self.sleep.tick(), 14400)
        await asyncio.wait_for(self.sleep.requests.get(), 1)
        self.send.assert_awaited_once_with(1)

    async def test_stop_cancels_and_clears_task(self):
        self.manager.start(1)
        await asyncio.wait_for(self.sleep.requests.get(), 1)
        self.assertTrue(await self.manager.stop(1))
        self.assertFalse(self.manager._tasks)
        self.assertFalse(await self.manager.stop(1))
        self.send.assert_not_awaited()

    async def test_stop_before_task_starts_clears_task(self):
        self.manager.start(1)
        await self.manager.stop(1)
        self.assertFalse(self.manager._tasks)

    async def test_restart_after_stop(self):
        self.manager.start(1)
        await self.manager.stop(1)
        self.assertTrue(self.manager.start(1))

    async def test_independent_chats_and_shutdown(self):
        self.manager.start(1)
        self.manager.start(2)
        tasks = list(self.manager._tasks.values())
        await self.manager.stop(1)
        self.assertIn(2, self.manager._tasks)
        await self.manager.close()
        self.assertFalse(self.manager._tasks)
        self.assertTrue(all(task.done() for task in tasks))

    async def test_blocked_destination_stops_notifications(self):
        self.send.side_effect = StopNotifications
        self.manager.start(1)
        task = self.manager._tasks[1]
        await self.sleep.tick()
        await asyncio.wait_for(task, 1)
        self.assertFalse(self.manager._tasks)

    async def test_temporary_failure_retries_next_interval_without_secret_logging(self):
        self.send.side_effect = [RuntimeError("fixture-secret"), None]
        self.manager.start(1)
        with self.assertLogs("weather_assistant.notifications", level="WARNING") as logs:
            await self.sleep.tick()
            await self.sleep.tick()
        await asyncio.wait_for(self.sleep.requests.get(), 1)
        self.assertEqual(self.send.await_count, 2)
        self.assertNotIn("fixture-secret", " ".join(logs.output))

    async def test_closed_manager_cannot_restart(self):
        await self.manager.close()
        with self.assertRaises(RuntimeError):
            self.manager.start(1)
