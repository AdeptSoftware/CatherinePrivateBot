import random

# ======== ========= ========= ========= ========= ========= ========= =========

def rnd_list(lst, default=""):
    match len(lst):
        case 0:
            return default
        case 1:
            return lst[0]
    index = random.randint(0, len(lst) - 1)
    return lst[index]

# ======== ========= ========= ========= ========= ========= ========= =========
