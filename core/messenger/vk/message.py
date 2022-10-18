#
from core.messenger.message import AbstractMessage

# ======== ========= ========= ========= ========= ========= ========= =========

class VkMessage(AbstractMessage):
    def __init__(self, item, fwd=True):
        super().__init__()
        self._text      = item["text"]
        self._item      = item
        self._fwd       = []

        if fwd:
            if "reply_message" in item:
                self._fwd += [VkMessage(item["reply_message"], False)]
            elif "fwd_messages" in item:
                for msg in item["fwd_messages"]:
                    self._fwd += [VkMessage(msg, False)]
            self._fwd  = tuple(self._fwd)

    @property
    def msg_id(self):
        return self._item["conversation_message_id"]

    @property
    def chat_id(self):
        return self._item["peer_id"]	# лучше передать peer_id

    @property
    def from_id(self):
        return self._item["from_id"]

    def is_bot(self):
        return self._item["from_id"] < 0

    @property
    def target_id(self):  # Для vk - это ID беседы
        return self._item["peer_id"]

# ======== ========= ========= ========= ========= ========= ========= =========
