import asyncio

async def countdown(name: str, n: int, *, sleep_time = 1):
 for i in range(n, -1, -1):
    print(f'{name}: {i}')
    await asyncio.sleep(sleep_time)


asyncio.run(countdown("first", 5))
