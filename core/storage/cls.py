# Базовые классы для работы с хранилищем данных
from core.safe import SafeVariable
import json

# ======== ========= ========= ========= ========= ========= ========= =========

FILE_ENCODING = "utf-8"

# ======== ========= ========= ========= ========= ========= ========= =========

# Все файлы, привязанные к таким объектам должны существовать на момент создания
class AbstractStorageObject:
	def __init__(self, path, immutable=False, default=""):
		self._obj  		= SafeVariable(default)
		self._immutable = immutable
		self._path 		= path
		self.restore()
	
	def get(self) -> SafeVariable:
		return self._obj
	
	# save_as - задайте полный путь, чтобы сделать копию файла под другим именем 
	def backup(self, save_as=None):
		if self._immutable:
			return False
		with self._obj:
			if type(self._obj.value) is str:
				string = self._obj.value
			else:
				string = json.dumps(self._obj.value, ensure_ascii=False)
			# запись и подготовка к ней
			return self._write(save_as or self._path, string)

	def restore(self):
		string = self._read(self._path)
		if not string:
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

	# create_storage_object
	def _cso(self, path, immutable, default) -> AbstractStorageObject:
		pass

	def mkdir(self, path):
		pass

	def exists(self, path):
		pass

	def get(self, path, is_json=True) -> AbstractStorageObject:
		pass

# ======== ========= ========= ========= ========= ========= ========= =========

class AbstractStorageManager(IStorageManager):
	_immutable_files = (
		"events.json",
		"auth.json"
	)

	def __init__(self):
		self._storage_objects = SafeVariable({})

	def get(self, path, is_json=True) -> AbstractStorageObject:
		with self._storage_objects:
			if path in self._storage_objects.value:
				return self._storage_objects[path]
		# Не было до этого запроса на получение этого файла.
		# Проверим существование необязательных объектов (если это он)
		immutable = path in self._immutable_files
		if not immutable:
			if not self.exists(path):
				self.create_file(path)
		# Создаем новый объект-хранения
		default = ""
		if is_json:
			default = {}
		storage_object = self._cso(path, immutable, default)
		# Регистрируем его
		with self._storage_objects:
			self._storage_objects[path] = storage_object
		return storage_object

# ======== ========= ========= ========= ========= ========= ========= =========
