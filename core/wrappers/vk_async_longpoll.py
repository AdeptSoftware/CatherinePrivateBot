# Стандартный VkBotLongPoll не мог в асинхронность
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import aiohttp
import asyncio

# ======== ========= ========= ========= ========= ========= ========= =========

class AsyncVkLongPoll(VkBotLongPoll):
    def __init__(self, vk, group_id, wait=25):
        super().__init__(vk, group_id, wait)
        self.session = aiohttp.ClientSession()

    # Проверка есть ли сообщения в чатах
    async def check(self):
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url,
                                   params=values,
                                   timeout=self.wait + 10) as res:
                response = await res.json()

            if 'failed' not in response:
                self.ts = response['ts']
                return [
                    self._parse_event(raw_event)
                    for raw_event in response['updates']
                ]

            elif response['failed'] == 1:
                self.ts = response['ts']
            elif response['failed'] == 2:
                self.update_longpoll_server(update_ts=False)
            elif response['failed'] == 3:
                self.update_longpoll_server()

        return []

    async def listen(self):
        while True:
            for event in await self.check():
                yield event

    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('Event registered must be a coroutine function')
        setattr(self, "event", coro)
        return coro

    async def start(self):
        async for event in self.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    asyncio.create_task(self.event(event.obj.message))

# ======== ========= ========= ========= ========= ========= ========= =========
