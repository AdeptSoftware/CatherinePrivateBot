from core.commands.command       import ACCESS_ADMIN, ACCESS_MODERATOR, ACCESS_ALL_AT_ONCE, \
                                        ACCESS_OCCUPIED, ACCESS_LOCK, ICommand
from core.commands.command_state import STATE_OVERLIMIT, STATE_ACCESS_DENIED
from core.safe                   import SafeVariable
from core.commands.context       import ContextEx

# ======== ========= ========= ========= ========= ========= ========= =========

# Безопасно управляет командами, отслеживает действия пользователей
class ChatCommand:
    def __init__(self, cmd: ICommand):
        self._states = SafeVariable([])
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

    def index(self, user_id):
        # Защищать self._states извне!
        for i in range(len(self._states)):
            if self._states[i].has_user(user_id):
                return i
        return None

    def _pop(self, index=None):
        if index is None or index >= len(self._states):
            return None
        return self._states.pop(index)

    def update(self, now):
        deleted = []
        rt = self._cmd.remember_time
        with self._states:
            for i in range(len(self._states)):
                if not self._states[i].update(now-rt):
                    deleted += [i]
            for i in deleted:
                self._states.pop(i)

    def status(self, now, user_id):
        """ Проверка статуса команды для текущего пользователя

        Перед вызовом функции убедитесь, что пользователь ведет диалог.
        Для этого можно использовать функцию has_dialog()

        После вызова функции check() проверка наличия пользователя не нужна

        :param now: текущее время (timestamp)
        :param user_id: ID пользователя
        :return: Код-статус, обозначающий готовность команды
        """
        with self._states:
            # Если команда оккупирована другим пользователем и он не 1 в списке
            index = self.index(user_id)
            if self._cmd.access_type == ACCESS_OCCUPIED and index != 0:
                if self._states[index].count > 1:
                    return STATE_OVERLIMIT    # Уже оповестили о том, что:
                return STATE_ACCESS_DENIED    # Используется другим user'ом
            return self._states[index].state(now)

    async def check(self, now, ctx: ContextEx):
        """ Поиск ответа среди команд """
        user_id = ctx.msg.from_id
        with self._states:  # Узкое место... Надо в будущем придумать что-нибудь
            self._cmd.on_enter()
            if self._cmd.access_type == ACCESS_LOCK and self._states:
                return None
            index = self.index(user_id)
            if index is None and self._cmd.access_type == ACCESS_ALL_AT_ONCE:
                index = 0
            state = self._pop(index) or self._cmd.create_state(now)
            node = await state.search(ctx)
            if node:
                if not self._states or self._cmd.access_type != ACCESS_ALL_AT_ONCE:
                    state.new_state(node, user_id, now)
                    self._states.insert(index or len(self._states), state)
                else:
                    self._states[0].new_state(node, user_id, now)
                return node
        return None

# ======== ========= ========= ========= ========= ========= ========= =========
