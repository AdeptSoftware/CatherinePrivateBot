from core.commands.command       import ICommand, ACCESS_ALL_AT_ONCE, ACCESS_PERSONAL
from core.wrappers.dialogflow    import DialogFlowAgent
from core.commands.command_state import ICommandState, CommandState
from core.commands.command_node  import ICommandNode

# ======== ========= ========= ========= ========= ========= ========= =========

class DialogFlowCommandState(ICommandState):
    def __init__(self, handler, now):
        # Меж.поточная защита self._last ведется из вне
        self._last      = CommandState(None, now)
        self._handler   = handler
        self._list      = []

    def new_state(self, node, user_id, now):
        for state in self._list:
            if state.name == node.name:
                state.new_state(node, user_id, now)
                self._last = state
                return
        self._last = CommandState(node, now)
        self._last.new_state(node, user_id, now)
        self._list += [self._last]

    def state(self, now):
        # Если self._last == None - на совести программиста
        # Так как при нормальных условиях до этого не должно дойти!
        return self._last.state(now)

    def has_user(self, user_id):
        for state in self._list:
            if state.has_user(user_id):
                return True
        return False

    @property
    def name(self):
        return self._last.name

    @property
    def count(self):
        return self._last.count

    def update(self, expired):
        deleted = []
        for i in range(len(self._list)):
            if not self._list[i].update(expired):
                deleted += [i]
        for index in deleted:
            self._list.pop(index)
        return len(self._list) != 0

    async def search(self, ctx):
        return await self._handler(ctx)

# ======== ========= ========= ========= ========= ========= ========= =========

class DialogFlowCommandNode(ICommandNode):
    def __init__(self, answer, cooldown, limit, name):
        self._cooldown  = max(cooldown, 0)
        self._limit     = max(limit, 0)
        self._answer    = answer
        self.__name__   = name

    @property
    def cooldown(self):
        return self._cooldown

    @property
    def limit(self):
        return self._limit

    def get(self, ctx):
        ctx.ans.set_text(self._answer)
        return True

# ======== ========= ========= ========= ========= ========= ========= =========

class DialogFlowCommand(ICommand):
    _agent = DialogFlowAgent()

    def __init__(self, name):
        self.__name__   = name
        self._threshold = 1.0

        self._data = {
            #       name                type           cd lim
            "Bad":              (ACCESS_PERSONAL,      60, 1),
            "IHateU":           (ACCESS_PERSONAL,      60, 1),
            "Lies":             (ACCESS_PERSONAL,      60, 1),
            "Love":             (ACCESS_PERSONAL,       5, 2),
            "Marry":            (ACCESS_PERSONAL,       5, 1),
            "MeaningLife":      (ACCESS_ALL_AT_ONCE,    5, 1),
            "Mood":             (ACCESS_ALL_AT_ONCE,    5, 1),
            "ReachAgreement":   (ACCESS_PERSONAL,       5, 1),
            "WhatsUp":          (ACCESS_ALL_AT_ONCE,    5, 1),
            "UPurpose":         (ACCESS_PERSONAL,       5, 1)
        }
        self._blocked = (
            "smalltalk.greetings.goodnight",
            "smalltalk.greetings.hello",
            "smalltalk.greetings.bye",
            "WhereIt"
        )

    def initialize(self, configs):
        self._agent.initialize(configs)
        self._threshold = configs["threshold"]

    @property
    def access_type(self):
        if self.__name__ in self._data:
            return self._data[self.__name__][0]
        return ACCESS_PERSONAL

    @property
    def name(self):
        return self.__name__

    def on_enter(self):
        self.__name__ = ""

    def create_state(self, now) -> ICommandState:
        return DialogFlowCommandState(self.check, now)

    async def check(self, ctx):
        if ctx.msg.items:
            result = self._agent.detect(ctx.msg.items.get())
            if result and result["score"] >= self._threshold:
                if result["action"] in self._blocked:
                    return None
                self.__name__ = result["action"]
                cooldown = limit = 0
                if result["action"] in self._data:
                    cooldown = self._data[result["action"]][1]
                    limit    = self._data[result["action"]][2]
                return DialogFlowCommandNode(
                    answer=result["text"],
                    cooldown=cooldown,
                    limit=limit,
                    name=result["action"]
                )
        return None

# ======== ========= ========= ========= ========= ========= ========= =========
