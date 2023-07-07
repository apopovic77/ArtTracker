import asyncio

class Dispatcher:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False

    async def add_task(self, coroutine):
        await self.queue.put(coroutine)
        if not self.is_running:
            await self.run()

    async def run(self):
        self.is_running = True
        while True:
            coroutine = await self.queue.get()
            task = asyncio.create_task(coroutine())
            await task