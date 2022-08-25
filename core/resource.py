# Классы для работы с ресурсами (json-файлами) приложения
from core.scripts.rand import rnd_list
import json

# ======== ========= ========= ========= ========= ========= ========= =========

class LanguageResource:
    def __init__(self, filename, encoding="utf-8"):
        with open(filename, 'r', encoding=encoding) as f:
            self._data = json.loads(f.read().encode(encoding))
        # Корректировка значений
        _list = []
        for name in self._data["CATHERINE"]:
            _list += [name.lower()]
        self._data["CATHERINE"] = _list
        # Подготовка списков
        self._split()

    def __getitem__(self, key):
        return self._data[key]

    # Вернёт одну из строк в списке
    def rnd(self, key: str):
        return rnd_list(self._data[key])

    def _split(self):
        for key in self._data:
            if key[0] == '#':
                _list = []
                _list += [value.lower().split(' ') for value in self._data[key]]
                self._data[key] = _list

# ======== ========= ========= ========= ========= ========= ========= =========
