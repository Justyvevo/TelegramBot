import asyncio
import time

async def countdown(name: str, n: int, *, sleep_time = 0.5):
 for i in range(n, -1, -1):
    print(f'{name}: {i}')
    await asyncio.sleep(sleep_time)


async def loundary():
    print("Запустили стирку")
    await countdown("Стиральная машинка", 3)
    print("Стирка закончена")

async def cooking():
    print("Поставили борщ")
    await countdown("Борщ на плите", 3)
    print("Борщ готов")

async def tea():
    print("Поставили чайник")
    await countdown("Чайник", 3)
    print("Чай готов")


asyncio.run(loundary())
time.sleep(1)
asyncio.run(cooking())
time.sleep(1)
asyncio.run(tea())

#Включает многие функции на старых версиях
from __future__ import annotations
