# Базовые классы для работы с хранилищем данных
from core.safe import SafeVariable
import json

# ======== ========= ========= ========= ========= ========= ========= =========

FILE_ENCODING = "utf-8"

# ======== ========= ========= ========= ========= ========= ========= =========

# Все файлы, привязанные к таким объектам должны существовать на момент создания
class AbstractStorageObject:
	def __init__(self, path, default):
		self._obj  = SafeVariable(default)
		self._path = path
		self.restore()
	
	def get(self) -> SafeVariable:
		return self._obj
	
	# save_as - задайте полный путь, чтобы сделать копию файла под другим именем 
	def backup(self, save_as=None):
		with self._obj:
			if type(self._obj.value) is str:
				string = self._obj.value
			else:
				string = json.dumps(self._obj.value, ensure_ascii=False)
			# запись и подготовка к ней
			return self._write(save_as or self._path, string)

	def restore(self):
		string = self._read(self._path)
		if string is None:
			return False
		# чтение прошло успешно
		with self._obj:
			if type(self._obj.value) is str:
				self._obj.value = string
			else:
				self._obj.value = json.loads(string.encode(FILE_ENCODING))
		return True

	def _read(self, path) -> str:
		pass

	def _write(self, path, string):
		pass

# ======== ========= ========= ========= ========= ========= ========= =========

# path - относительный путь (по отношению к root)
class IStorageManager:
	def create(self):								   # аргументы не добавлять!
		pass

	def create_file(self, path, string=""):
		pass

	def mkdir(self, path):
		pass

	def exists(self, path):
		pass

	# На основе существующего файла
	def create_storage_object(self, path, is_json=True) -> AbstractStorageObject:
		pass

	cso = create_storage_object							# shortcut

# ======== ========= ========= ========= ========= ========= ========= =========
