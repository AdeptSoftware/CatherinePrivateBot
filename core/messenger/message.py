#
from core.messenger.parser import MessageParser


# ======== ========= ========= ========= ========= ========= ========= =========

class AbstractMessage(MessageParser):
    def is_me(self):
        pass

    @property
    def target_id(self):
        """ Проверка того, что сообщение из чата разрешено """
        return 0

    @property
    def msg_id(self):       # да знаю, что это уже больше абстрактный класс
        return 0            # но это немного упрощает вызовы в CommandManager

    @property
    def from_id(self):
        return 0

    @property
    def chat_id(self):
        return 0

    def is_bot(self):
        pass

# ======== ========= ========= ========= ========= ========= ========= =========
