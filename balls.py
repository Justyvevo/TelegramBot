import asyncio

async def loundary():
    print("Запустили стирку")
    await asyncio.sleep(1)
    print("Стирка закончена")

async def cooking():
    print("Поставили борщ")
    await asyncio.sleep(1)
    print("Борщ готов")

async def tea():
    print("Поставили чайник")
    await asyncio.sleep(1)
    print("Чай готов")

async def main():
   await asyncio.gather(loundary(), cooking(), tea())

asyncio.run(main())

