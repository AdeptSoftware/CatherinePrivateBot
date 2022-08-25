# Класс, обновляющий различные данные
import core.safe
import datetime
import asyncio

# ======== ========= ========= ========= ========= ========= ========= =========

def _default_on_error_handler(data=None): print("Error: " + str(data))

G_ON_ERROR = _default_on_error_handler           # Глобальный обработчик событий
G_TIMEZONE = 0                                   # Use: core.updater.G_TIMEZONE

# ======== ========= ========= ========= ========= ========= ========= =========

def time():
    return datetime.datetime.now() + datetime.timedelta(hours=G_TIMEZONE)

def timezone():
    return G_TIMEZONE

async def sleep(sec):
    await asyncio.sleep(sec)

# ======== ========= ========= ========= ========= ========= ========= =========

async def error(data=None):
    G_ON_ERROR(data)
    await asyncio.sleep(1)
    return False

# ======== ========= ========= ========= ========= ========= ========= =========

class Updater:
    def __init__(self, delay=1):
        self._tasks     = core.safe.SafeVariable([])
        self._delay     = delay
        self._loop      = asyncio.new_event_loop()
        self._exit      = True

    def run(self):
        """ Запуск с блокированием текущего потока """
        if self._exit:
            self._exit = False
            self._loop.run_until_complete(self._updater())

    async def _updater(self):
        while True:
            deleted = []
            with self._tasks:
                for task in self._tasks:
                    if self._exit:
                        return
                    if task[1]:     # isn't working?
                        task[1] = None
                        asyncio.create_task(self._caller(task))
                    elif task[1] is not None:
                        deleted += [task]
                for task in deleted:
                    self._tasks.remove(task)
            await asyncio.sleep(self._delay)

    @staticmethod
    async def _caller(task):
        try:
            task[1] = await task[0]()
        except Exception as err:
            task[1] = await error(err)

    def stop(self):
        self._exit = True
        # Завершится поток немного позже

    @property
    def loop(self):
        return self._loop

    def append(self, callback):
        """ Присоединяет новый callback к списку задач

        :param callback: функция: async fn() -> boolean.

        Если функция вернёт:

        True - функция будет использована повторно
        False - функция будет удалена после выполнения
        """
        with self._tasks:
            self._tasks += [[callback, True]]

# ======== ========= ========= ========= ========= ========= ========= =========
