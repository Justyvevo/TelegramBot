"""One cancellable notification task per private chat, owned by the application."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

log = logging.getLogger(__name__)


class StopNotifications(Exception):
    """The destination is no longer reachable (for example, the bot was blocked)."""


class NotificationManager:
    def __init__(
        self,
        send: Callable[[int], Awaitable[None]],
        interval: float,
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if interval <= 0:
            raise ValueError("Notification interval must be positive.")
        self._send, self._interval, self._sleep = send, interval, sleep
        self._tasks: dict[int, asyncio.Task[None]] = {}
        self._closed = False

    def start(self, chat_id: int) -> bool:
        if self._closed:
            raise RuntimeError("Notification manager is closed.")
        task = self._tasks.get(chat_id)
        if task is not None and not task.done():
            return False
        self._tasks[chat_id] = asyncio.create_task(self._run(chat_id))
        return True

    async def _run(self, chat_id: int) -> None:
        try:
            while True:
                await self._sleep(self._interval)
                try:
                    await self._send(chat_id)
                except StopNotifications:
                    return
                except Exception:
                    # Do not log request URLs, credentials, city names or chat identifiers.
                    log.warning("Notification failed; will retry at the next interval.")
        finally:
            if self._tasks.get(chat_id) is asyncio.current_task():
                self._tasks.pop(chat_id, None)

    async def stop(self, chat_id: int) -> bool:
        task = self._tasks.pop(chat_id, None)
        if task is None:
            return False
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return True

    async def close(self) -> None:
        self._closed = True
        tasks = list(self._tasks.values())
        self._tasks.clear()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
