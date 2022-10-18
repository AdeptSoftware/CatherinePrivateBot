#
from core.storage.cls                   import IStorageManager
from core.resource                      import LanguageResource
from core.updater                       import Updater
from core.event                         import EventManager
from core.messenger.answer              import IAnswer
from core.messenger.message             import AbstractMessage

# Применяется для хранения важных классов приложения и доступа к ним
class CommonData:
    def __init__(self):
        self.storage        = None                      # IStorageManager
        self.updater        = None                      # Updater
        self.messengers     = []                        # AbstractMessengers
        self.events         = None                      # EventManager
        self.lang           = None                      # LanguageResource

# ======== ========= ========= ========= ========= ========= ========= =========

# Передается в CommandManager. Для каждого мессенджера свой
class Context:
    def __init__(self, msgr, data: CommonData, mngr):
        # Общие поля
        self._common        = data
        # Поля связанные с мессенджером
        self._messenger     = msgr                      # AbstractMessenger
        self._commands      = mngr                      # CommandManager
        # Дополнительные поля. Для различных нужд
        self.data           = None

    @property
    def storage(self) -> IStorageManager:
        return self._common.storage

    @property
    def updater(self) -> Updater:
        return self._common.updater

    @property
    def messengers(self):
        return self._common.messengers

    @property
    def events(self) -> EventManager:
        return self._common.events

    @property
    def lang(self) -> LanguageResource:
        return self._common.lang

    @property
    def msgr(self):
        return self._messenger

    @property
    def mngr(self):
        return self._commands


# ======== ========= ========= ========= ========= ========= ========= =========

# Должен быть свой у каждого сообщения AbstractMessenger'а
class ContextEx(Context):
    def __init__(self, ctx, msg, ans):
        super().__init__(ctx.msgr, ctx.__dict__["_common"], ctx.mngr)
        self._message = msg                             # AbstractMessage
        self._answer  = ans                             # IAnswer

    @property
    def msg(self) -> AbstractMessage:
        return self._message

    @property
    def ans(self) -> IAnswer:
        return self._answer

# ======== ========= ========= ========= ========= ========= ========= =========
