#
import pymorphy2 # http://opencorpora.org/dict.php?act=gram

# ======== ========= ========= ========= ========= ========= ========= =========

class TextElement:
    _morph = pymorphy2.MorphAnalyzer()

    def __init__(self, text, index=None):
        self._lower = text.lower()
        self._index = index
        self._text  = text
        self._parse = None

    @property
    def lower(self):
        return self._lower

    @property
    def text(self):
        return self._text

    @property
    def index(self):
        return self._index

    # При помощи вот этого можно обращаться к MorphAnalyzer().parse()
    def __getattr__(self, item):
        if self._parse is None:
            self._parse = self._morph.parse(self._text)[0]
        if hasattr(self._parse, item):
            return getattr(self._parse, item)
        return getattr(self._lower, item)

    def __repr__(self):
        return "<\"{}\": {}>".format(self._text, self.tag)

    def __getitem__(self, index):
        return self._lower[index]

    def __eq__(self, other):
        return self._lower == other

    def __ne__(self, other):
        return self._lower != other

# ======== ========= ========= ========= ========= ========= ========= =========

class TextList:
    def __init__(self, lst=None):
        self._list      = []               # Например: ["Примечание", "#", "1a"]
        self._sentences = None

        if lst:
            if type(lst) is TextList:
                self._list  = lst
            else:
                for index in range(len(lst)):
                    self._list += [TextElement(lst[index], index)]

    def contain(self, values):
        """ Проверка содержит ли сообщение хотя бы 1 слово

        :param values: список слов в lowercase формате
        :return: None/Word
        """
        for v in values:
            if v in self._list:
                return True
        return False

    def contain_all(self, values):
        """ Проверка содержит ли сообщение все слова

        :param values: список слов в lowercase формате
        :return: None/Word
        """
        for v in values:
            if v not in self._list:
                return False
        return True

    def find(self, values, start=0, stop=None, index=False):
        """ Поиск значений

        :param index: возвращать index или сам объект
        :param values: список, которых ищем
        :param start: начальная позиция
        :param stop: конечная позиция
        :return: :class:`TextElement` or None
        """
        for i in range(start, stop or len(self._list)):
            if self._list[i].lower in values:
                if index:
                    return i
                return self._list[i]
        return None

    # phrases - должен содержать lowercase фразы
    def has_phrases(self, phrases, word_order_matters=True):
        """ Проверка содержит ли сообщение определенные фразы

        :param phrases: список фраз в lowercase формате.
            phrase состоит из списка слов
        :param word_order_matters: важен порядок слов или нет
        :return: 0 = None/Phrase
        """
        length = len(self._list)
        for i in range(length):
            for phrase in phrases:
                if word_order_matters:
                    end = len(phrase)+i
                    if end > length:
                        continue
                    if phrase == self[i:end]:
                        return phrase
                elif self.contain_all(phrase):
                    return phrase
        return None

    def get(self, start=0, end=None, ignore_parasite=False):
        """ Выдаёт строку по индексу слов/символов

        :param start: индекс начала
        :param end: индекс конца
        :param ignore_parasite: слова-паразиты - междометия
        """
        res = ""
        i   = start
        end = end or len(self._list)
        while i < end:
            if not ignore_parasite or "INTJ" not in self._list[i].tag:
                text = self._list[i].text
                if res and (text.isalpha() or text == '-' or text.isdigit()):
                    res += ' '
                res += text
            elif i+1 < end and "PNCT" not in self._list[i].tag:
                i += 1
            i += 1
        return res

    @property
    def sentences(self):
        """ Список предложений """
        if self._sentences is None:
            lst = []
            for start, end in self.boundary(self._list):
                lst += [TextList(self._list[start:end+1])]
            self._sentences = tuple(lst)
        return self._sentences

    @staticmethod
    def boundary(_list):
        """ Границы предложений """
        last = 0
        length = len(_list)
        for i in range(length):
            for char in ".?!":
                if char in _list[i]:
                    yield last, i
                    last = i+1
        if last != length:
            yield last, length-1

    def __add__(self, other: list):
        self._list += other
        return self

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i) -> TextElement:
        return self._list[i]

    def __repr__(self):
        return str(self._list)

# ======== ========= ========= ========= ========= ========= ========= =========
