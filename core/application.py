#
import datetime
import signal

# ======== ========= ========= ========= ========= ========= ========= =========
# Обработчики по умолчанию

async def _std_err(data=None):
    print("Error: " + str(data))
    return False


async def _std_msg(ctx):
    pass

def _std_log(text, console=True, output=True):
    """
    :param text: выводимый текст
    :param console: выводить в консоль?
    :param output: выводить куда-то еще (кроме консоли: в файл/облако/т.д.)?
    :return:
    """
    if console or output:
        print(text)

# ======== ========= ========= ========= ========= ========= ========= =========

class Application:
    # Обработчики событий и переопределяемые функции:
    on_terminate    = None      # fn(data: CommonData)      -> None
    on_message      = _std_msg  # async fn(ctx: ContextEx)  -> None
    on_error        = _std_err  # async fn(data=None)       -> False
    log             = _std_log  # fn(text, console, output) -> None
    # Прочие поля
    _timezone       = 0

    def __init__(self, data, timezone=0):
        """
        :param data: :class:`CommonData`
        """
        Application.log(data.lang["INIT"])
        signal.signal(signal.SIGTERM, self._terminate)
        signal.signal(signal.SIGINT,  self._terminate)
        # Прочие данные
        self._timezone  = timezone
        self._data      = data

    @staticmethod
    def timezone():
        return Application._timezone

    @staticmethod
    def time():
        return datetime.datetime.now() + \
               datetime.timedelta(hours=Application._timezone)

    # Heroku перезагружает скрипты раз в 24ч+rand(0,216)мин
    # Посылает сигнал SIGTERM. А через 30 секунд сигнал SIGKILL.
    # То есть у нас есть 30 сек для сохранения разного рода информации
    # перед тем, как приложение принудительно закроют.
    def _terminate(self, *args):
        if self.on_terminate:
            self.on_terminate(self._data)
        Application.log(self._data.lang["TERMINATE"])
        exit(0)

    def run(self):
        Application.log(self._data.lang["RUN"], output=False)
        self._data.updater.run()

# ======== ========= ========= ========= ========= ========= ========= =========
