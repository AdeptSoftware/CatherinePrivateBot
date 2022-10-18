# Классы для работы с локальным хранилищем
from core.storage.cls import *
import os

# ======== ========= ========= ========= ========= ========= ========= =========

def _write(path, string):
	with open(path, 'w', encoding=FILE_ENCODING) as f:
		f.write(string)
		return True

# ======== ========= ========= ========= ========= ========= ========= =========

# Благодаря этому объекту, доступ к общим для потоков данных - безопасен
# Все файлы, привязанные к таким объектам должны существовать на момент создания
class LocalStorageObject(AbstractStorageObject):
	def _read(self, path):
		with open(self._path, 'r', encoding=FILE_ENCODING) as f:
			return f.read()

	def _write(self, path, string):
		return _write(path, string)

# ======== ========= ========= ========= ========= ========= ========= =========

# Класс, управляющий локальным хранилищем.
class LocalStorageManager(AbstractStorageManager):
	# path - относительный путь (по отношению к root)
	def __init__(self, root):
		super().__init__()
		self._root = root

	def create(self):
		return True

	def create_file(self, path, string=""):
		return _write(self._root+path, string)

	def mkdir(self, path):
		os.mkdir(self._root+path)

	def exists(self, path):
		return os.path.exists(self._root+path)

	def _cso(self, path, immutable, default) -> AbstractStorageObject:
		return LocalStorageObject(self._root+path, immutable, default)

# ======== ========= ========= ========= ========= ========= ========= =========
