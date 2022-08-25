#
from core.messenger.answer import IAnswer
import json

# ======== ========= ========= ========= ========= ========= ========= =========

MAX_MSG_SIZE = 4000
MAX_ATT_SIZE = 10

# ======== ========= ========= ========= ========= ========= ========= =========

class VkAnswer(IAnswer):
    def __init__(self, peer_id, msg_id=0):
        self._peer_id           = peer_id
        self._message_id        = msg_id
        self._sticker_id        = 0
        self._text              = ""
        self._reply             = ""
        self._attachments       = []

    def get(self):
        if not self._text and \
           not self._attachments and \
           not self._sticker_id:
            return None

        return {
            "attachment":       ','.join(self._attachments),
            "sticker_id":       self._sticker_id,
            "peer_id":          self._peer_id,
            "forward":          self._reply,
            "message":          self._text,
            "dont_parse_links": True,
            "random_id":        0
        }

    def set_text(self, text):
        self._text += text
        if len(self._text) > MAX_MSG_SIZE:
            r_string = "..."+self._text[MAX_MSG_SIZE:]
            self._text = self._text[:MAX_MSG_SIZE]+"..."
            return r_string
        return None

    def set(self, **kwargs):
        if "sticker_id" in kwargs:
            self._sticker_id = kwargs["sticker_id"]
        return None

    def set_image(self, image, filename=None):
        return self._set_attachment(image)

    def set_document(self, url, filename=None):
        return self._set_attachment(url)

    def set_audio(self, audio):
        return self._set_attachment(audio)

    def set_video(self, video):
        return self._set_attachment(video)

    def _set_attachment(self, obj):
        self._attachments += [obj]
        if len(self._attachments) > MAX_ATT_SIZE:
            r_att = self._attachments[MAX_ATT_SIZE:]
            self._attachments = self._attachments[:MAX_ATT_SIZE]
            return r_att
        return None

    def reply(self):
        obj = {
            "peer_id":                  self._peer_id,
            "conversation_message_ids": "[{0}]".format(self._message_id)
        }
        self._reply = json.dumps(self._reply)
        return None

# ======== ========= ========= ========= ========= ========= ========= =========
