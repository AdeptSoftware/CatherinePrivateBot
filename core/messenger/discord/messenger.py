#
from core.messenger.messenger           import AbstractMessenger, TYPE_DISCORD
from core.messenger.discord.message     import DiscordMessage
from core.messenger.discord.answer      import DiscordAnswer
from core.commands.context              import ContextEx

from discord.ext				        import commands
from discord                            import Intents

# ======== ========= ========= ========= ========= ========= ========= =========

class DiscordMessenger(AbstractMessenger):
    def __init__(self, data, configs):
        super().__init__(data, configs)
        self._bot   = commands.Bot(command_prefix=configs["prefix"],
                                   intents=Intents.default(),
                                   loop=data.updater.loop)
        self._token = configs["token"]

        @self._bot.event
        async def on_message(item):
            ctx = None
            try:
                ctx = ContextEx(
                    self._ctx,
                    DiscordMessage(item),
                    DiscordAnswer(item.guild.id)
                )
                if await ctx.mngr.on_message(ctx):
                    await self.send(ctx.ans.get(), item)
            except Exception as err:
                await self._error(err, ctx)

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
