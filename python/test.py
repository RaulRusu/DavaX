import asyncio

class AsyncRange:
    def __init__(self, start, end):
        self.data = range(start, end)

    async def __aiter__(self):
        for index in self.data:
            await asyncio.sleep(0.5)
            yield index

async def main():
    it = AsyncRange(0, 5)
    ait = it.__aiter__()
    try:
        while True:
            value = await ait.__anext__()
            print(value)
    except StopAsyncIteration as sai:
        print('stop')



asyncio.run(main())