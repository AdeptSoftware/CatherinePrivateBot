from core.commands.command       import ACCESS_ADMIN, ACCESS_MODERATOR, ACCESS_ALL_AT_ONCE, \
                                        ACCESS_OCCUPIED, ICommand
from core.commands.command_state import STATE_OVERLIMIT, STATE_ACCESS_DENIED
from core.safe                   import SafeVariable
from core.commands.context       import ContextEx

# ======== ========= ========= ========= ========= ========= ========= =========


class _State:
    def __init__(self, node, now):
        self._node  = node          # Текущий ICommandNode
        self._count = 0             # Количество использований команды
        self._prev  = now           # Время предпоследнего вызова
        self._last  = 0             # Время последнего вызова

    async def search(self, ctx):
        return await self._node.check(ctx) or await self._node.find(ctx)


# ======== ========= ========= ========= ========= ========= ========= =========

# Безопасно управляет командами, отслеживает действия пользователей
class ChatCommand:
    def __init__(self, cmd: ICommand):
        self._states = SafeVariable({})
        self._cmd    = cmd

    @property
    def name(self):
        return self._cmd.name

    def appeal(self):
        return self._cmd.appeal

    def has_access(self, user_access_type):
        """ Проверка уровня доступа пользователя к команде """
        if self._cmd.access_type == ACCESS_ADMIN:
            return user_access_type == ACCESS_ADMIN
        if self._cmd.access_type == ACCESS_MODERATOR:
            return user_access_type >= ACCESS_MODERATOR
        return True

    def has_dialog(self, user_id):
        """ Пользователь(и) уже ведёт диалог с нами? """
        if self._cmd.access_type == ACCESS_ALL_AT_ONCE:
            user_id = 0
        with self._states:
            return user_id in self._states.value

    def update(self, now):
        deleted = []
        rt = self._cmd.remember_time
        with self._states:
            for user_id in self._states.value:
                if not self._states[user_id].update(now-rt):
                    deleted += [user_id]
            for user_id in deleted:
                self._states.pop(user_id)

    def status(self, now, user_id):
        """ Проверка статуса команды для текущего пользователя

        Перед вызовом функции убедитесь, что пользователь ведет диалог.
        Для этого можно использовать функцию has_dialog()

        После вызова функции check() проверка наличия пользователя не нужна

        :param now: текущее время (timestamp)
        :param user_id: ID пользователя
        :return: Код-статус, обозначающий готовность команды
        """
        if self._cmd.access_type == ACCESS_ALL_AT_ONCE:
            user_id = 0
        with self._states:
            # Если команда оккупирована другим пользователем и он не 1 в списке
            if self._cmd.access_type == ACCESS_OCCUPIED and \
               user_id != list(self._states.keys())[0]:
                if self._states[user_id].count > 1:
                    return STATE_OVERLIMIT    # Уже оповестили о том, что:
                return STATE_ACCESS_DENIED    # Используется другим user'ом
            return self._states[user_id].state(now)

    async def check(self, now, ctx: ContextEx):
        """ Поиск ответа среди команд """
        state = self._cmd.create_state(now)
        with self._states:
            for _id in (ctx.msg.from_id, 0):
                if _id in self._states.value:
                    state = self._states[_id]
                    break
        # Проверка команды
        node = await state.search(ctx)
        if node:
            state.new_state(node, now)
            # Сохранение нового состояния
            from_id = 0
            if self._cmd.access_type != ACCESS_ALL_AT_ONCE:
                from_id = ctx.msg.from_id
            with self._states:
                self._states[from_id] = state
            return node
        return None

# ======== ========= ========= ========= ========= ========= ========= =========
