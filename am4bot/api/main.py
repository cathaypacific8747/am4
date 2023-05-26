import asyncio

async def main():
    print('hello world!')

asyncio.get_event_loop().run_until_complete(main())