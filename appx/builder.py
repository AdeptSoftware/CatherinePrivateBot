# 14.06.2022
from core.storage.yadisk_storage        import YandexStorageManager
from core.storage.local_storage         import LocalStorageManager
from core.messenger.discord.messenger   import DiscordMessenger
from core.messenger.vk.messenger        import VkMessenger
from core.event                         import EventManager
from core.commands.context 		        import CommonData, Context
from core.resource                      import LanguageResource
import core.updater                     as _u

import appx.command_list
import appx.events

import core.debug
import json

# ======== ========= ========= ========= ========= ========= ========= =========

class _Application:
    def __init__(self, data: CommonData):
        print(data.lang["INIT"])
        self._data = data

    def run(self):
        print(self._data.lang["RUN"])
        self._data.updater.run()

# ======== ========= ========= ========= ========= ========= ========= =========

class AppBuilder:
    # data, lang - пути до файлов
    def __init__(self, data, lang):
        self._data              = self.load(data)
        self._auth              = None
        # Обработчики
        self._event_loader      = None
        # AppData variables
        self._app               = CommonData()
        self._app.lang          = LanguageResource(lang)
        self._app.updater       = _u.Updater()

        appx.command_list.attach()

    def get(self) -> _Application:
        """ :return: Возвращает объект приложения """
        _u.G_TIMEZONE = self._auth["timezone"]
        if self._event_loader:
            self._event_loader(self._app)
        return _Application(self._app)

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
        self._auth = storage.create_storage_object("auth.json").get()
        with self._auth:
            # Инициализация мессенджеров
            # СЮДА ДОБАВИТЬ ДРУГИЕ МЕССЕНДЖЕРЫ, ЕСЛИ ТО БУДЕТ ТРЕБОВАТЬСЯ
            cls = [VkMessenger, DiscordMessenger]
            for cfg in self._auth["messengers"]:
                msgr = cls[cfg["type"]](self._app, cfg)
                self._app.messengers += [msgr]

    def use_debug(self):
        """ Инициализация объекта для вывода логов и отладки """
        out = self._app.storage.create_storage_object(self._data["log"], False)
        with self._auth:
            core.debug.init(out)
        # Оповещение о запуске
        core.debug.get().log(self._app.lang["INIT"], True)

    def use_events(self):
        """
        Создает объект менеджера событий и устанавливает обработчик загрузки
        событий
        """
        self._event_loader = appx.events.loader
        self._app.events   = EventManager(self._app.updater)

    def use_dialogflow(self):
        with self._auth:
            appx.command_list.dialogflow_init(self._auth["dialogflow"])

# ======== ========= ========= ========= ========= ========= ========= =========
