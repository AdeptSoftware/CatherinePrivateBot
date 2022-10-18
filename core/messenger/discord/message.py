#
from core.messenger.message import AbstractMessage

# ======== ========= ========= ========= ========= ========= ========= =========

class DiscordMessage(AbstractMessage):
    def __init__(self, ctx, fwd=True, appeal=False):
        super().__init__()
        self._text   = ctx.content
        self._appeal = appeal
        self._ctx    = ctx
        self._fwd    = []

        if fwd and self._ctx.reference:
            self._fwd += [DiscordMessage(self._ctx.reference.resolved, False)]

    @property
    def msg_id(self):
        return self._ctx.id

    @property
    def chat_id(self):
        return self._ctx.channel.id

    @property
    def from_id(self):
        return self._ctx.author.id

    def is_bot(self):
        return self._ctx.author.bot

    @property
    def target_id(self):    # Для дискорда - это ID сервера
        return self._ctx.guild.id

# ======== ========= ========= ========= ========= ========= ========= =========
