# Производные классы предназначены для организации цикла сообщений
from core.commands.manager import CommandManager
from core.commands.context import Context
from core.updater          import error

# ======== ========= ========= ========= ========= ========= ========= =========

# Message Types:
TYPE_VK					= 0
TYPE_DISCORD			= 1

# ======== ========= ========= ========= ========= ========= ========= =========

class AbstractMessenger:
    def __init__(self, data, configs):
        self._ctx = Context(self, data, CommandManager(data.updater, configs))
        data.updater.append(self._run)

    @staticmethod
    async def _error(err, ctx):
        text = ""
        if ctx:
            text = ctx.msg.text.replace('\n', ' ')
            text = "{0}: \"{1}\"".format(ctx.msg.from_id, text)
        return await error(text or err)

    # Уникальный идентификатор (см. выше: Message Types)
    @property
    def type_id(self):
        return 0

    @property
    def bot_id(self):
        return 0

    # Аргументы не добавлять!
    async def _run(self):
        pass

    def create_answer(self, chat_id):
        pass

    def send(self, obj):
        pass

# ======== ========= ========= ========= ========= ========= ========= =========
