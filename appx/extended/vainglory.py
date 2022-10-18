import random


# Не больше 40!
# Разлагает число на возможные суммы слагаемых
def _decomposition(number, index=1, ret=[]):
    value = sum(ret) + index
    if value > number:
        return []
    elif value == number:
        return [ret + [index]]
    else:
        lst = []
        _r = ret + [index]
        while index < number:
            result = _decomposition(number, index+1, _r)
            if result:
                lst += result
            index += 1
        return lst


# term_count - количество слагаемых в числе number
def decomposition(number, term_count):
    lst = []
    index = 1
    while index < number:
        for obj in _decomposition(number, index):
            if len(obj) == term_count:
                lst += [obj]
        index += 1
    return lst


def rnd(lst):
    return random.randint(0, len(lst) - 1)

def rnd2(start, end, step):
    return rnd(list(range(start, end, step)))

def add(lst, value):
    for i in range(len(lst)):
        lst[i] += value

def balancer(players):
    if players == 1:
        return [random.randint(1, 10)]
    elif players == 2:
        num = random.randint(1, 20)
        return [-num, num]
    elif players == 3:
        num = random.randint(3, 30)
        lst = decomposition(num, 2)
        return [-num] + lst[rnd(lst)]
    elif players == 4:
        num = random.randint(5, 30)
        lst = decomposition(num, 2)
        index1 = index2 = rnd(lst)
        while index1 == index2:
            index2 = rnd(lst)
        for i in range(2):
            lst[index1][i] = -lst[index1][i]
        return lst[index1] + lst[index2]
    elif players == 5:
        num = random.randint(9, 30)
        lst1 = decomposition(num, 2)
        lst2 = decomposition(num, 3)
        while True:
            flag = True
            index1 = rnd(lst1)
            index2 = rnd(lst2)
            if index1 != index2:
                for value in lst1[index1]:
                    if value in lst2[index2]:
                        flag = False
                        break
            if flag:
                for i in range(2):
                    lst1[index1][i] = -lst1[index1][i]
                return lst1[index1] + lst2[index2]
    return []


def generate(team1, team2, _default=1200):
    _min = _max = team1
    if team2 > team1:
        _max = team2
    else:
        _min = team2
    if _min < 0 or _max > 5:
        return None
    # Совместная игра
    if team1 == 0 or team2 == 0:
        lst = balancer(_max)
        if lst:
            for i in range(_max):
                lst[i] += _default
            if team1:
                return [lst, []]
            return [[], lst]
        return None
    # Балансировка матчей по командам
    offset  = random.randint(20, 50)
    lst = balancer(_max)
    if team1 == team2 == 1:
        add(lst, _default+offset)
        return [lst, lst]
    # Кол-во elo требуемое для баланса
    if _min > 1:
        k = _max/_min   # коэффициент
        # Коррекция дробных значений
        while int(offset*k) != offset*k:
            offset += 1

        while True:
            flag = True
            lst2 = balancer(_min)
            for value in lst2:
                if value in lst:
                    flag = False
                    break
            if flag:
                break
        add(lst2, _default+int(offset*k))
    else:
        lst2 = [_default+(offset*len(lst))]
    add(lst, _default+offset)
    if team1 == _min:
        return [lst2, lst]
    return [lst, lst2]

"""
def rprint(i, j, p):
    _max = max(i, j)
    if p is not None:
        score0 = (sum(p[0])+(1200*(_max-i)))/_max
        score1 = (sum(p[1])+(1200*(_max-j)))/_max
        print(i, "vs", j, score0, score1, p)
    else:
        print(i, "vs", j, None)

def run():
    for j in range(0, 6):
        for i in range(0, 7):
            rprint(i, j, generate(i, j))
"""
