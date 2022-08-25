# Производные классы предназначены для формирования ответа на сообщения

class IAnswer:
    def get(self):
        pass

    def set_text(self, text):
        pass

    # Специфическое
    def set(self, **kwargs):
        pass

    def set_image(self, image, filename=None):
        pass

    def set_document(self, url, filename=None):
        pass

    def set_audio(self, audio):
        pass

    def set_video(self, video):
        pass

    def reply(self):
        pass

# ======== ========= ========= ========= ========= ========= ========= =========
