# Классы для работы с событиями
from core.safe    import SafeVariable
import asyncio
import time

# ======== ========= ========= ========= ========= ========= ========= =========

# Просто структура для хранения данных события
class Event:
    def __init__(self, fn, data, cooldown, expired):
        self.fn         = fn
        self.data       = data
        self.cooldown   = cooldown
        self.expired    = expired
        self.reserve    = None

# ======== ========= ========= ========= ========= ========= ========= =========

# Выполняет различные задачи в заданное время с определенным интервалом
class EventManager:
    def __init__(self, updater, delay=15):
        self._events = SafeVariable({})
        self._delay  = delay
        updater.append(self._update)

    def new_ex(self, name, fn, delay, cooldown, data=None):
        """ Создает новое событие

        :param name: уникальное имя события (если такое есть - перезапишется)
        :param fn: функция-обработчик (Если вернет False - событие будет удалено)
        :param delay: когда следующий вызов события (через сколько sec)
        :param cooldown: время между событиями (sec)
        :param data: дополнительные данные
        :return: True/False
        """
        if delay < 0 or cooldown <= 0:
            return False

        with self._events:
            # Оборачиваем в SafeVariable, чтобы безопасно использовать get()
            self._events[name] = SafeVariable(
                Event(fn, data, cooldown, time.time()+delay)
            )
        return True

    def new(self, fn, obj):
        """ Пример содержания для obj см. new_ex() """
        return self.new_ex(obj["name"], fn, obj["delay"], obj["cooldown"], obj["data"])

    def delete(self, name):
        with self._events:
            if name in self._events.value:
                self._events.pop(name)
                return True
        return False

    def get(self, name):
        """
        Пример использования полученного события:
        with event: event["fn"](event.value)
        """
        with self._events:
            if name in self._events.value:
                return self._events[name]
        return None

    def keys(self):
        with self._events:
            return self._events.keys()

    async def _update(self):
        while True:
            deleted = []
            now = time.time()
            with self._events:
                for name in self._events.value:
                    event = self._events[name]
                    with event:
                        if now >= event.expired:
                            if not event.fn(event.value):
                                # Удаляем события, которые вернули False
                                deleted += [name]
                            else:
                                event.expired = now+event.cooldown
                if deleted:
                    for name in deleted:
                        self._events.pop(name)
            await asyncio.sleep(self._delay)

# ======== ========= ========= ========= ========= ========= ========= =========
