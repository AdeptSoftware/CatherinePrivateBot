#
from core.commands.command_node     import CommandNode
from core.commands.command_state    import CommandState, ICommandState

# ======== ========= ========= ========= ========= ========= ========= =========

# Типы доступа пользователей к команде
ACCESS_LOCK                 = -1    # Блокирует команду на время после использования
ACCESS_USER                 = 0     # Default: обычный пользователь
ACCESS_PERSONAL             = 0     # Отвечает каждому по отдельности
ACCESS_ALL_AT_ONCE          = 1     # Отвечает всем сразу
ACCESS_OCCUPIED             = 2     # Отвечает только одному
ACCESS_MODERATOR            = 3     # Отвечает только модерам
ACCESS_ADMIN                = 4     # Отвечает только админам

# ======== ========= ========= ========= ========= ========= ========= =========

_COMMANDS   = []    # Общий список команд, доступный всем мессенджерам
_DEFAULT_RT = 20    # Значение времени запоминания по умолчанию

# регистрирует команду
def add(cmd):
    global _COMMANDS
    _COMMANDS += [cmd]

# создает новую командую
def new(condition, answer, cooldown=0, limit=0, access_type=0, remember_time=60,
        name="", nodes=None, appeal=True):
    if remember_time < cooldown:
        remember_time = cooldown + (_DEFAULT_RT*int(limit > 0))
    root = CommandNode(condition, answer, cooldown, limit, nodes)
    add(Command(root, access_type, remember_time, name, appeal))
    return True

# Возвращает список команд
def get_commands():
    return _COMMANDS

# ======== ========= ========= ========= ========= ========= ========= =========

class ICommand:
    @property
    def appeal(self):
        return True

    @property
    def access_type(self):
        return ACCESS_PERSONAL

    @property
    def remember_time(self):
        return _DEFAULT_RT

    @property
    def name(self):
        return ""

    def on_enter(self): # Опциональное
        pass

    def create_state(self, now) -> ICommandState:
        pass

# ======== ========= ========= ========= ========= ========= ========= =========

class Command(ICommand):
    # Если cooldown > remember_time, то команда будет удалена не достигнув конца cooldown
    def __init__(self, node, access_type=0, remember_time=_DEFAULT_RT, name="", appeal=True):
        """
        :param node: :class: `core.commands.command.CommandNode`
        :param access_type: тип доступа пользователя к команде
        :param remember_time: сколько секунд команда будет запомненной
        :param name: имя команды (уникальное)
        :param appeal: срабатывает только при наличии обращения/общения с ботом
        """
        self._remember_time = max(remember_time, 1) # нужно хотя бы немного времени
        self._access_type   = access_type           # см. в начале файла
        self._appeal        = appeal
        self._node          = node
        self._node.rename(name)

    @property
    def appeal(self):
        return self._appeal

    @property
    def access_type(self):
        return self._access_type

    @property
    def remember_time(self):
        return self._remember_time

    @property
    def name(self):
        return self._node.name

    def create_state(self, now) -> ICommandState:
        return CommandState(self._node, now)

# ======== ========= ========= ========= ========= ========= ========= =========
