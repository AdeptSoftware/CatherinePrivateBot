# 26.05.2022 Объект-singleton. Для вывода логов и ошибок
import core.application
import traceback
import sys

# ======== ========= ========= ========= ========= ========= ========= =========

class _Debug:
    def __init__(self, storage_object, output2console=True):
        self._output2console = output2console   # Принудительно блокирует вывод в консоль
        self._so             = storage_object
        self._last           = None

    def log(self, text, console=True, output=True):
        """ Выводит текст в логи """
        time = core.application.Application.time()
        text = time.strftime("[%Y-%m-%d %H:%M:%S]: ") + text
        # Вывод в файл
        if output:
            try:
                out = self._so.get()
                with out:
                    out += text + '\n'
                self._so.backup()
            except Exception as exc:
                text += "\n" + str(exc)
        # Вывод в консоль
        if self._output2console and console:
            print(text)

    async def async_err(self, data=None):
        self.err(data)

    def err(self, data=None):
        """ Собираем всю доступную информацию и сохраняет в логах.
            Если ошибка повторилась, то повторной отправки не будет """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        calls = ""
        # cause = str(exc_value)
        cause = f"{exc_type.__name__}: {str(exc_value)}"
        try:
            for frame in traceback.extract_tb(exc_traceback):
                index = frame.filename.rfind('\\')
                calls += "=> {0}.{1}():{2} ".format(frame.filename[index + 1:-3], frame.name, frame.lineno)
        except UnicodeDecodeError:
            # Если с кодировкой все ОК. Пользователь никогда этого сообщения не увидит
            print("Проверить кодировку всех файлов! Она должна быть UTF-8!")
            return
        # Сохраняем?
        if self._last == cause+calls:
            return
        self._last = cause+calls
        if data and str(data) not in cause:
            result = f"{data}\n{cause} {calls}"
        else:
            result = f"{cause}\n{calls}"
        self.log(result)

# ======== ========= ========= ========= ========= ========= ========= =========

_G_DEBUG = None

# ======== ========= ========= ========= ========= ========= ========= =========

def init(storage_object):
    global _G_DEBUG
    if _G_DEBUG is None:
        _G_DEBUG = _Debug(storage_object)
        # установка обработчиков ошибок и логов
        core.application.Application.on_error = _G_DEBUG.async_err
        core.application.Application.log      = _G_DEBUG.log
    return _G_DEBUG

def get():
    return _G_DEBUG

# ======== ========= ========= ========= ========= ========= ========= =========
