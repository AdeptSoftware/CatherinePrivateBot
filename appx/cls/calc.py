import random
import math
import re


# ======== ========= ========= ========= ========= ========= ========= =========

_fn_name = re.compile(r"[a-z]+")      # в math нет функций с _ подчёркиванием!
_formula = re.compile(r"[(\da-z][(\d+\-*×х∙^/÷:%., )<a-z>!=]+")
_func    = ["rand"]

# ======== ========= ========= ========= ========= ========= ========= =========

def get_expressions(string):
    _list = []
    for obj in _formula.finditer(string):
        start, end = obj.span()
        text = string[start:end].replace(' ', '')
        if text and not text.isdigit():
            _list += [text]
    return _list

def rand(a, b=0, repeat=1):
    result = 0
    repeat = min(max(repeat, 0), 1000)
    if a > b:
        a, b = b, a
    for i in range(repeat):
        result += random.randint(a, b)
    return result

# ======== ========= ========= ========= ========= ========= ========= =========

# Необходимо передавать всегда текст в формате lowercase
class Calculator:
    def __init__(self, expression):
        self._expr = expression.replace(':', '/')\
                               .replace('÷', '/')\
                               .replace('×', '*')\
                               .replace('х', '*')\
                               .replace('∙', '*')\
                               .replace('^', '**')

    def result(self):
        # Не безопасная функция конечно, но так манит...
        # Надеюсь набор ограничений поможет...
        if not self._check():
            return None
        try:
            return eval(self._expr)
        except SyntaxError:
            return None
        except AttributeError:
            return None

    def _check(self):
        offset = 0
        for obj in _fn_name.finditer(self._expr):
            start, end = obj.span()
            text = self._expr[start+offset:end+offset]
            flag = text in _func
            if not hasattr(math, text) and not flag:
                return False
            if not flag:
                text = "math."+text
            self._expr = self._expr[:start+offset]+text+self._expr[end+offset:]
            offset += 5
        return True


# ======== ========= ========= ========= ========= ========= ========= =========
