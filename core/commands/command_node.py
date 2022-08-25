#

# ======== ========= ========= ========= ========= ========= ========= =========

# У каждого производного класса должно быть уникальное имя в self.__name__
class ICommandNode:
    @property
    def cooldown(self):
        return 0

    @property
    def limit(self):
        return 0

    @property
    def name(self):
        return self.__name__

    async def check(self, ctx):
        return None

    async def find(self, ctx):
        return None

    def get(self, ctx):
        pass

# ======== ========= ========= ========= ========= ========= ========= =========

class CommandNode(ICommandNode):
    # condition - функция вида: fn(ctx)->boolean
    # answer - имя строки в базе строк или функция обработчик вида: fn(ctx)->boolean
    def __init__(self, condition, answer, cooldown=0, limit=0, nodes=None):
        self._cooldown              = max(cooldown, 0)
        self._limit                 = max(limit, 0)
        self._condition             = condition
        self._answer                = answer
        self._nodes                 = nodes or []
        self.__name__               = ""

    def rename(self, name):
        self.__name__ = name
        for i in range(len(self._nodes)):
            self._nodes[i].__name__ = "{}:{}".format(self.__name__, i)

    @property
    def cooldown(self):
        return self._cooldown

    @property
    def limit(self):
        return self._limit

    async def check(self, ctx):
        """ Проверка подходит ли текущий CommandNode

        :param ctx: :class: `core.commands.context.ContextEx
        :return: None or CommandNode object
        """
        if await self._condition(ctx):
            return self
        return None

    async def find(self, ctx):
        """ Поиск подходящего дочернего CommandNode

        :param ctx: :class: `core.commands.context.ContextEx
        :return: None or CommandNode object
        """
        for node in self._nodes:
            if await node.check(ctx):
                return node
        return None

    def get(self, ctx):
        """ Возвращает ответ на команду """
        if type(self._answer) is str:
            ctx.ans.set_text(ctx.lang.rnd(self._answer))
        else:
            self._answer(ctx)

# ======== ========= ========= ========= ========= ========= ========= =========
