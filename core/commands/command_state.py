#

# Состояние команды
STATE_ACCESS_DENIED       = -1            # Команда не доступна (исп. и тд)
STATE_COOLDOWN            = 0             # Команда на откате
STATE_LIMIT               = 1             # Достигнут лимит по использованию
STATE_OVERLIMIT           = 2             # Кол-во исп. больше отметки лимита
STATE_READY               = 3             # Команда доступна

# ======== ========= ========= ========= ========= ========= ========= =========

# Определяет и управляет текущим состоянием команды
class ICommandState:
    def new_state(self, node, user_id, now):
        pass

    def has_user(self, user_id):
        pass

    def state(self, now):
        pass

    @property
    def name(self):
        return ""

    @property
    def count(self):
        return 0

    def update(self, expired):
        pass

    async def search(self, ctx):
        pass

# ======== ========= ========= ========= ========= ========= ========= =========

class CommandState(ICommandState):
    def __init__(self, node, now):
        self._node      = node         # Текущий ICommandNode
        self._count     = 0            # Количество использований команды
        self._prev      = 0            # Время предпоследнего вызова
        self._last      = now          # Время последнего вызова
        self._users     = []

    def new_state(self, node, user_id, now):
        if self._node.name != node.name:
            self._count = 0
            self._last  = now

        if user_id not in self._users:
            self._users += [user_id]

        self._prev      = self._last
        self._node      = node
        self._last      = now
        self._count    += 1

    def has_user(self, user_id):
        return user_id in self._users

    def state(self, now):
        if self._node.limit:
            if self._count == self._node.limit+1:
                return STATE_LIMIT
            elif self._count > self._node.limit+1:
                return STATE_OVERLIMIT
        if (not self._node.limit and now != self._prev) or \
           (self._node.limit and now != self._last):       # Только что изменено
            if self._node.cooldown and now < self._prev + self._node.cooldown:
                return STATE_COOLDOWN
        return STATE_READY

    # expired - возможно не совсем корректное название
    # expired = now-remember_time из выражения: now < last+remember_time
    def update(self, expired):
        # Если вернет False, то состояние будет удалено. Пользователь молчит
        return expired < self._last

    @property
    def name(self):
        return self._node.name

    @property
    def count(self):
        return self._count

    async def search(self, ctx):
        node = await self._node.check(ctx)
        if node is None and self._count:
            node = await self._node.find(ctx)
        return node

# ======== ========= ========= ========= ========= ========= ========= =========
