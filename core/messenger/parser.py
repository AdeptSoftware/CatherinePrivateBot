#
from core.xlist import *
import re

# ======== ========= ========= ========= ========= ========= ========= =========

# Регулярное выражение для разбивки сообщения на части
_parts = re.compile(r"[\w\d][-\w\d]+|[_\w\d]+|\[id\d+\|.+?]|@[_\w\d]+")

# ======== ========= ========= ========= ========= ========= ========= =========

class MessageParser:
    def __init__(self, text="", fwd=None):
        self._list   = TextList()
        self._fwd    = fwd or []
        self._appeal = False
        self._text   = text
        self._prefix = ""

    @property
    def appeal(self):
        """ Вернет строку, как обращаются к нам """
        return self._appeal

    @property
    def items(self):
        """ Вернёт разбитое на слова и другие символы сообщение """
        return self._list

    @property
    def prefix(self):
        """ Вернёт символы перед сообщением """
        return self._prefix

    @property
    def text(self):
        return self._text

    @property
    def fwd(self):
        return self._fwd

    def parse(self, names, bot_id=0):
        """ Преобразование текста в список символов

        :param names: список имён бота
        :param bot_id: ID бота
        """
        if not self._list and self._text:
            self._list = TextList(self.__appeal(self.__split(), names, bot_id))

    # Разбивает текст на части
    def __split(self):
        last = 0
        lst = []
        for obj in _parts.finditer(self._text):
            start, end = obj.span()
            if start-last > 0:
                self.__punctuation(lst, last, start)
            lst += [obj.group()]
            last = end
        if last < len(self._text):
            self.__punctuation(lst, last, len(self._text))
        return lst

    # Убирает пробелы, манипулирует пунктуацией
    def __punctuation(self, lst, start, end):
        symbols = self._text[start:end].replace(' ', '')
        if symbols:
            if lst:
                lst += [symbols]
            else:
                self._prefix = symbols
        return []

    # Проверка обращения в тексте и пересланных сообщениях
    def __appeal(self, lst, names, bot_id):
        for start, end in TextList.boundary(lst):
            self._mark(lst, start, +1, names)
            self._mark(lst, end,   -1, names)
        if not self._appeal:
            for msg in self._fwd:
                if msg.from_id == bot_id:
                    self._appeal = True
                    break
        lst = list(filter(None, lst))
        if lst and not self._prefix and not lst[0][0].isalnum():
            self._prefix = lst.pop(0)
        return lst

    # Помечает символы для удаления + проверка наличия обращения
    def _mark(self, lst, index, offset, names):
        length = len(lst)
        while 0 <= index < length and lst[index] and not lst[index].isalnum():
            index += offset
        # Могли установить в None ранее
        if lst[index] and lst[index].lower() in names:
            lst[index] = None
            index += offset
            if 0 <= index < length and ',' in lst[index]:
                lst[index] = lst[index].replace(',', '') or None
            self._appeal = True

# ======== ========= ========= ========= ========= ========= ========= =========
