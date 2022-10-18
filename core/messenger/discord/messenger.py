#
from core.messenger.messenger           import AbstractMessenger, TYPE_DISCORD
from core.messenger.discord.message     import DiscordMessage
from core.messenger.discord.answer      import DiscordAnswer
from core.commands.context              import ContextEx

from discord.ext                        import commands
from discord                            import Intents

# ======== ========= ========= ========= ========= ========= ========= =========

class DiscordMessenger(AbstractMessenger):
    def __init__(self, data, configs):
        super().__init__(data, configs)
        intents       = Intents(messages=True, guilds=True)
        self._bot     = commands.Bot(command_prefix=configs["prefix"],
                                     loop=data.updater.loop,
                                     intents=intents)
        self._token   = configs["token"]

        @self._bot.event
        async def on_message(item):
            # К сожалению, с 31.08.2022 вступает в силу ограничение
            # Команды бота доступны либо через @self._bot.command()
            # Либо если есть упоминание бота / пересланное сообщение
            # Ограничение можно снять, если бот будет на >= 100 серверах
            ctx = None
            try:
                if item.content is None:
                    return
                ctx = ContextEx(
                    self._ctx,
                    DiscordMessage(item, appeal=True),
                    DiscordAnswer(item.guild.id)
                )
                if await ctx.mngr.on_message(ctx):
                    await self.send(ctx.ans.get(), item)
                await self._on_message(ctx)
            except Exception as err:
                await self._on_error(err, ctx)

    @property
    def type_id(self):
        return TYPE_DISCORD

    @property
    def bot_id(self):
        return self._bot.user.id

    def create_answer(self, chat_id):
        return DiscordAnswer(chat_id)

    async def _run(self):
        await self._bot.start(self._token)
        return True

    def send(self, obj, item=None):
        if item and item.guild.id == obj["chat_id"]:
            if obj["reply"]:  # Пересылать можно только в текущий чат
                return item.reply(obj["text"], embed=obj["embed"], files=obj["files"])
            channel = item.channel
        else:
            channel = self._bot.get_channel(obj["chat_id"])
        return channel.send(obj["text"], embed=obj["embed"], files=obj["files"])

# ======== ========= ========= ========= ========= ========= ========= =========
