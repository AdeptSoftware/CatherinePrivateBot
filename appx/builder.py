# 14.06.2022
from core.storage.yadisk_storage        import YandexStorageManager
from core.storage.local_storage         import LocalStorageManager
from core.messenger.discord.messenger   import DiscordMessenger
from core.messenger.vk.messenger        import VkMessenger
from core.event                         import EventManager
from core.commands.context 		        import CommonData
from core.resource                      import LanguageResource
from core.application                   import Application

import core.updater                     as _u
import appx.command_list
import appx.events

import core.debug
import json

# ======== ========= ========= ========= ========= ========= ========= =========

class AppBuilder:
    # data, lang - пути до файлов
    def __init__(self, data, lang):
        # AppData variables
        self._app               = CommonData()
        self._app.lang          = LanguageResource(lang)
        self._app.updater       = _u.Updater()
        # Содержимое файлов
        self._data              = self.load(data)
        self._auth              = None
        # Обработчики
        self._event_loader      = None

        appx.command_list.attach()

    def get(self) -> Application:
        """ :return: Возвращает объект приложения """
        return Application(self._app, self._auth["timezone"])

    @property
    def auth(self):
        """ :return: SafeVariable объект, содержащий данные аутентификации """
        return self._auth

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return json.loads(f.read())

    def use_local_storage(self):
        self.use_storage(LocalStorageManager(self._data["src"]))

    def use_yandex_storage(self):
        token = self._data["token"]
        self.use_storage(YandexStorageManager(self._data["dst"], token))

    def use_storage(self, storage):
        """ Инициализирует хранилище и настраивает мессенджеры

        :param storage: :class:`core.storage.cls.IStorageManager`
        """
        if not storage.create():
            raise Exception(self._app.lang["INIT_FAILED"])
        self._app.storage = storage
        self._auth = storage.get("auth.json").get()
        with self._auth:
            # Инициализация мессенджеров
            # СЮДА ДОБАВИТЬ ДРУГИЕ МЕССЕНДЖЕРЫ, ЕСЛИ ТО БУДЕТ ТРЕБОВАТЬСЯ
            cls = [VkMessenger, DiscordMessenger]
            for cfg in self._auth["messengers"]:
                msgr = cls[cfg["type"]](self._app, cfg)
                self._app.messengers += [msgr]

    def use_debug(self):
        """ Инициализация объекта для вывода логов и отладки """
        core.debug.init(self._app.storage.get(self._data["log"], False))

    def use_events(self, filename="events.json"):
        """
        Создает объект менеджера событий и устанавливает обработчик загрузки
        событий
        """
        self._app.events = EventManager(self._app.updater)
        appx.events.loader(self._app, filename)

    def use_dialogflow(self):
        with self._auth:
            appx.command_list.dialogflow_init(self._auth["dialogflow"])

# ======== ========= ========= ========= ========= ========= ========= =========
