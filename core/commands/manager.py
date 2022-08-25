# Заготовка под центр управлением командами
from core.commands.chat_manager  import ChatManager
from core.commands.resentment    import ResentmentController
from core.commands.context       import ContextEx
from core.commands.command_state import STATE_ACCESS_DENIED, STATE_LIMIT, \
                                        STATE_READY
import time

# ======== ========= ========= ========= ========= ========= ========= =========

class CommandManager:
    def __init__(self, updater, configs):
        self._resentment = ResentmentController(configs["resentment"])
        self._chats      = {}
        for key in configs["targets"]:
            self._chats[int(key)] = ChatManager(configs["targets"][key])

        updater.append(self._update)

    async def _update(self):
        now = time.time()
        self._resentment.update(now)
        for key in self._chats:
            for cmd in self._chats[key].commands:
                cmd.update(now)
        return True

    # P.S.: Не стал объединять проверки через "or", т.к. читаемость будет хуже
    async def on_message(self, ctx: ContextEx):
        # Сообщение из запрещенного сервера?
        if ctx.msg.target_id not in self._chats:
            return False
        # Сообщение от бота?
        if ctx.msg.is_bot():
            return False
        # Пользователь обидел нас?
        if self._resentment.check_resentment(ctx.msg.from_id):
            return False
        chat = self._chats[ctx.msg.target_id]
        # Пользователь заблокирован (запрещено ему отвечать)?
        if chat.is_blacklist_user(ctx.msg.from_id):
            return False
        # # # Стадия проверки команд # # #
        now = time.time()
        ctx.msg.parse(ctx.lang["CATHERINE"], ctx.msgr.bot_id)
        has_dialog = chat.has_dialog(ctx.msg.from_id) or ctx.msg.appeal
        user_access_type = chat.get_user_access_type(ctx.msg.from_id)
        for cmd in chat.commands:
            # Важно ли, чтобы пользователь обращался к нам/уже вёл диалог
            # Если да, то проверяем, что с нами уже ведут беседу
            if cmd.appeal() and not has_dialog:
                continue
            # Проверка условий срабатывания команды на сообщение пользователя
            node = await cmd.check(now, ctx)
            if node is None:
                continue
            # Пользователь допущен к команде?
            if not cmd.has_access(user_access_type):
                continue
            # # # Проверка прошла успешно # # #
            # Проверим готовность команды
            # Q: Почему проверяем статус команды сейчас, а не перед cmd.check()?
            # A: Дело в том, что не можем быть уверены, что это та самая команда
            status = cmd.status(now, ctx.msg.from_id)
            if status == STATE_ACCESS_DENIED:
                ctx.ans.set_text(ctx.lang.rnd("CMD_ACCESS_DENIED"))
                return True
            if status == STATE_LIMIT:
                ctx.ans.set_text(ctx.lang.rnd("CMD_LIMIT"))
                return True
            if status == STATE_READY:
                node.get(ctx)
                return True
            # На STATE_COOLDOWN и STATE_OVERLIMIT - никак не реагируем
            return False
        return False
