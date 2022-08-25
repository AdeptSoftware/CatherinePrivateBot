#
from core.messenger.answer  import IAnswer
from discord                import File

import mimetypes
import requests
import io

# ======== ========= ========= ========= ========= ========= ========= =========

class DiscordAnswer(IAnswer):
    def __init__(self, chat_id):
        self._text      = ""
        self._embed     = None
        self._files     = []
        self._reply     = False
        self._chat_id   = chat_id
        self._links     = []

    def get(self):
        if not self._text and \
           not self._embed:
            return None

        return {
            "embed":    self._embed,
            "files":    self._files,
            "text":     self._text + '\n' + "\n".join(self._links),
            "reply":    self._reply,
            "chat_id":  self._chat_id
        }

    def set_text(self, text):
        self._text += text
        return None

    def set_image(self, url, filename=None):
        self.set_document(url, filename)

    def set_document(self, url, filename=None):
        response = requests.get(url=url)
        if response.status_code == requests.codes.ok:
            if filename is None:
                mime = response.headers.get("content-type") or ""
                filename = "file"+mimetypes.guess_extension(mime)
            file = io.BytesIO(response.content)
            self._files += [File(fp=file, filename=filename)]
        return None

    # Не поддерживается
    def set_audio(self, url):
        return None

    def set(self, **kwargs):
        if "embed" in kwargs:
            self._embed = kwargs["embed"]
        return None

    def set_video(self, url):
        self._links += [url]
        return None

    def reply(self):
        self._reply = True
        return None

# ======== ========= ========= ========= ========= ========= ========= =========
