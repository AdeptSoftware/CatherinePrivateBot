# Классы для работы с облачным хранилищем
from core.storage.cls			import *
from core.wrappers.yandex_disk	import YandexDiskAPI
from core.safe					import SafeVariable

# ======== ========= ========= ========= ========= ========= ========= =========

# Благодаря этому объекту, доступ к общим для потоков данных - безопасен
# Все файлы, привязанные к таким объектам должны существовать на момент создания
class YandexStorageObject(AbstractStorageObject):
	def __init__(self, api, path, immutable, default):
		self._api = api
		super().__init__(path, immutable, default)

	def _read(self, path):
		with self._api:
			return self._api.download(path)

	def _write(self, path, string):
		with self._api:
			return self._api.upload(path, string)

# ======== ========= ========= ========= ========= ========= ========= =========

# Класс, управляющий облачным хранилищем.
class YandexStorageManager(AbstractStorageManager):
	# path - относительный путь (по отношению к root)
	def __init__(self, root, token):
		super().__init__()
		self._token = token
		self._root	= root
		self._api	= None

	def create(self):
		if self._api is None:
			self._api = SafeVariable(YandexDiskAPI(self._token, FILE_ENCODING))
		return self._api.check_token()

	def create_file(self, path, string=""):
		with self._api:
			return self._api.upload(self._root+path, string)

	def mkdir(self, path):
		with self._api:
			return self._api.mkdir(self._root+path)

	def exists(self, path):
		with self._api:
			return self._api.exists(self._root+path)

	def _cso(self, path, immutable, default) -> AbstractStorageObject:
		return YandexStorageObject(self._api, self._root+path, immutable, default)
			
# ======== ========= ========= ========= ========= ========= ========= =========
