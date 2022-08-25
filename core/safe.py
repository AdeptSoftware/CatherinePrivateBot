import threading

# ======== ========= ========= ========= ========= ========= ========= =========

# Пример
# x = SafeVariable(0)                       x = SafeVariable([2, 3, 5])
# with x:                                   with x:
#   x += 2                                      x += [7, 11, 13]
# print(x.value)                    или     print(x())

# Не поддерживает итерацию объектов (используйте SafeVariable.value)
class SafeVariable:
    def __init__(self, value):
        self.value = value
        self._lock = threading.RLock()

    # ==== ========= ========= ========= ========= ========= ========= =========
    # Эти функции вызываются всегда, даже при ошибках

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    # ==== ========= ========= ========= ========= ========= ========= =========

    def __str__(self):
        return str(self.value)

    # ==== ========= ========= ========= ========= ========= ========= =========

    def __call__(self):
        return self.value

    def __getattr__(self, item):
        return self.value.__getattribute__(item)

    # ==== ========= ========= ========= ========= ========= ========= =========

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __len__(self):
        return len(self.value)

    # ==== ========= ========= ========= ========= ========= ========= =========

    def __add__(self, other):
        self.value += other
        return self

    def __radd__(self, other):
        self.value = other + self.value
        return self

    # Другие операции добавлю по мере необходимости...

# ======== ========= ========= ========= ========= ========= ========= =========
