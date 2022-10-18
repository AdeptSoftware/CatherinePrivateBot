# Обёртка для YandexDisk API
import yadisk
import io

# ======== ========= ========= ========= ========= ========= ========= =========

class YandexDiskAPI:
    def __init__(self, token, encoding):
        self._api       = yadisk.YaDisk(token=token)
        self._encoding  = encoding

    def check_token(self):
        return self._api.check_token()

    def upload(self, path, string, overwrite=True):
        bytes_io = io.BytesIO(string.encode())
        self._api.upload(bytes_io, path, overwrite=overwrite)
        bytes_io.close()
        return True

    def download(self, path):
        bytes_io = io.BytesIO(b"")
        self._api.download(path, bytes_io)
        string = bytes_io.getvalue().decode(self._encoding, 'backslashreplace')
        bytes_io.close()
        return string

    def exists(self, path):
        return self._api.exists(path)

    def mkdir(self, path):
        return self._api.mkdir(path)

# ======== ========= ========= ========= ========= ========= ========= =========
