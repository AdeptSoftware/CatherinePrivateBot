# Класс, контролирующий доступность команд пользователям
from core.safe import SafeVariable
import random
import time

# Минимальное и максимальное время обиды на пользователя
_MIN = 86400*2    # 2 дня
_MAX = 86400*5    # 5 дней

# ======== ========= ========= ========= ========= ========= ========= =========

class ResentmentController:
    def __init__(self, users):
        # Список на кого обижены
        self._resentment = SafeVariable(users)

    def update(self, now):
        deleted = []
        with self._resentment:
            for user_id in self._resentment.value:
                if now >= self._resentment[user_id]:
                    deleted += [user_id]
            for user_id in deleted:
                self._resentment.pop(user_id)

    def check_resentment(self, user_id):
        with self._resentment:
            return user_id in self._resentment.value

    def set_resentment(self, user_id):
        expired = time.time() + random.randint(_MIN, _MAX)
        with self._resentment:
            self._resentment[user_id] = expired

    def forgive_resentment(self, user_id):
        with self._resentment:
            if user_id in self._resentment.value:
                self._resentment.pop(user_id)
                return True
        return False

# ======== ========= ========= ========= ========= ========= ========= =========
