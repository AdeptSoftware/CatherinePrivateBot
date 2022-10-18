﻿# Используемые команды приложением
import core.messenger.messenger     as _msgr
import core.commands.command        as _cmd
import core.commands.context        as _ctx
import core.scripts.rand            as _rnd
import core.application             as _app
import core.xlist                   as _x

import appx.extended.vainglory      as _vg

import appx.cls.dialogflow_command  as _dlg
import appx.scripts.convert         as _conv
import appx.scripts.maps            as _maps
import appx.cls.calc                as _calc

import datetime
import aiohttp
import random
import re

# ======== ========= ========= ========= ========= ========= ========= =========

async def hello(ctx: _ctx.ContextEx):
    return ctx.msg.items.contain(ctx.lang["$HELLO"])

async def goodbye(ctx: _ctx.ContextEx):
    if ctx.msg.items:
        return ctx.msg.items.has_phrases(ctx.lang["#GOODBYE"]) or \
              (ctx.msg.items[0].lower in ctx.lang["$GOODBYE2"] and len(ctx.msg.items) == 1)
    return False
    # Проблема слова "пока" в том, что оно не только обозначает прощание...

async def sleep(ctx: _ctx.ContextEx):
    return ctx.msg.items.has_phrases(ctx.lang["#SLEEP"])

# ======== ========= ========= ========= ========= ========= ========= =========

async def calculate(ctx: _ctx.ContextEx):
    ctx.data    = []
    expressions = _calc.get_expressions(ctx.msg.text.lower())
    for expr in expressions:
        result = _calc.Calculator(expr).result()
        if result is not None:
            ctx.data += ["{0} = {1}".format(expr, result)]
    return len(ctx.data) != 0

async def acronym(ctx: _ctx.ContextEx):
    result = ctx.msg.items.has_phrases(ctx.lang["#ACRONYM"])
    if result:
        pos = len(result)
        if pos < len(ctx.msg.items):
            word    = ctx.msg.items[pos].lower
            headers = {"User-Agent": "Mozilla/5.0"}
            acr     = ""
            for char in word:
                acr += '%'+str(char.encode("cp1251"))[4:6]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url="http://www.korova.ru/humor/cyborg.php?acronym="+acr,
                    headers=headers
                ) as res:
                    if not res.ok:
                        return False
                    text = await res.text("cp1251")
            end   = text.find("</p>\r\n<form action")
            start = text[:end].rfind("<p>")
            text  = text[start:end]
            if text[:10] == "ВАСЯПУПКИН":
                return False
            ctx.data = text[len(word)+6:]   # 6 = "<p>:  "
            return True
    return False

# ======== ========= ========= ========= ========= ========= ========= =========

async def date(ctx: _ctx.ContextEx):
    result = ctx.msg.items.has_phrases(ctx.lang["#DATE"], False)
    if result:
        delta = 0
        flag  = True
        time_offset = ctx.lang["TIME_OFFSET"]
        for word in ctx.msg.items:
            if word in time_offset:
                delta = time_offset.index(word)-2
                flag  = False
                break
        now  = _app.Application.time()+datetime.timedelta(days=delta)
        plus = '+'*(_app.Application.timezone() >= 0)
        fmt = "%d/%m/%Y" + " %H:%M"*int(flag)
        ctx.data = now.strftime(fmt)
        if flag:
            ctx.data += f" (UTC {plus}{_app.Application.timezone()}:00)"
        return True
    return False

async def is_true(ctx: _ctx.ContextEx):
    if ctx.msg.items:
        return ctx.msg.items.contain(ctx.lang["$TRUE"]) and \
               ctx.msg.text[-1] == '?'
    return False

async def repeat(ctx: _ctx.ContextEx):
    _list = ctx.msg.items
    if _list and _list[0] in ctx.lang["$REPEAT"]:
        if random.random() <= 0.35:                     # Вредничаем
            ctx.data = ctx.lang.rnd("=REPEAT")
        else:
            sym = ""
            start, end = 1, len(_list)
            if end > 1 and _list[1] in ('\"', ":\""):   # Если есть "область"
                start += 1
                for i in range(start, end):
                    if '\"' in _list[i]:
                        end = i
                        index = _list[i].find('\"')     # Отделение: ?" -> ?
                        if index > 0:
                            sym = _list[i][:index]
                        break
            ctx.data = ctx.msg.items.get(start, end)+sym
            ctx.data = ctx.data[0].upper() + ctx.data[1:]
        return True
    return False

async def variants(ctx: _ctx.ContextEx):
    _or   = ctx.lang["$OR"].copy()
    _list = ctx.msg.items
    if _list.contain(_or):
        parts = []
        _or += [","]
        start = int(_list[0].lower in ctx.lang["$WHO"] or
                    _list[0].lower in ctx.lang["$WHAT"])
        while True:
            end    = _list.find(_or, start, index=True)
            text   = ctx.msg.items.get(start, end or len(_list))
            parts += [text.replace('?', '')]
            if end is None:
                break
            start  = end+1
        parts = list(filter(None, parts))
        if len(parts) > 1:
            ctx.data = _rnd.rnd_list(parts)
            if ctx.lang["CATHERINE"] or ctx.lang["$ME"] == ctx.data:
                ctx.data = ctx.lang["$YOU"]
            ctx.data = ctx.data[0].upper() + ctx.data[1:]
            return True
    return False

async def hit(ctx: _ctx.ContextEx):
    _list = ctx.msg.items
    if _list:
        ctx.data = None
        nouns    = ctx.lang["$HIT_NOUN"]
        normal   = _list[0].normal_form
        if normal in ctx.lang["$HIT_VERB"]:
            if ctx.msg.fwd:
                if len(ctx.msg.fwd) > 1:
                    ctx.data = ctx.lang.rnd("=HITS")
                    return True
                pass
            else:
                _all  = ctx.lang["$HIT_ALL"]
                _me   = ctx.lang["$HIT_ME"]
                _self  = [ctx.lang["$HIT_SELF"]]
                _self  += ctx.lang["CATHERINE"]
                for i in range(1, len(_list)):
                    if "NOUN" in _list[i].tag:
                        normal = _list[i].normal_form
                        if normal not in nouns:
                            ctx.data = _list[i].inflect({"nomn", "sing"}).word
                            ctx.data = ctx.data.capitalize()
                            break
                    elif "LATN" in _list[i].tag:
                        ctx.data = _list[i].text.capitalize()
                        break
                    elif _list[i] in _self or _list[i] == _all:
                        ctx.data = ctx.lang.rnd("=NO_HIT")
                        return True
                    elif _list[i] == _me:
                        ctx.data = ctx.lang.rnd("=HIT_ME")
                        return True
        if ctx.data:
            index = _list.find(nouns, 1, index=True) or 0
            ctx.data = ctx.lang.rnd("=HIT").format(ctx.data, nouns[index])
            ctx.data = ctx.data[0].upper() + ctx.data[1:]
            return True
    return False

# ======== ========= ========= ========= ========= ========= ========= =========

async def where(ctx: _ctx.ContextEx):
    if ctx.msg.items and ctx.lang["$WHERE"] == ctx.msg.items[0]:
        for attempt in range(5):
            result = await _maps.rnd_place()
            if result:
                if "status_code" in result:
                    ctx.data = ctx.lang.rnd("TOO_MANY_REQUESTS")
                else:
                    ctx.data = result
                return True
        ctx.data = ctx.lang.rnd("=WHERE")
        return True
    return False

async def who(ctx: _ctx.ContextEx):
    return ctx.lang["$WHO"] in ctx.msg.items

async def how_much(ctx: _ctx.ContextEx):
    span = {
        "#HOW_MANY_TIMES":   (1,    25),    # Должно быть перед #HOW_MUCH
        "#HOW_MUCH":         (1,   100),
        "#HOW_OFTEN":        (1,     8),
        "#HOW_LONG":       (300, 86400)
    }
    for name in span:
        if ctx.msg.items.has_phrases(ctx.lang[name]):
            cnt = random.randint(span[name][0], span[name][1])
            units = ctx.lang["TIME_UNIT"]
            if name == "#HOW_LONG":
                ctx.data = ""
                obj = _conv.sec2smh(cnt)
                for key in obj:
                    if obj[key] > 0:                  # ед.    # сокращение
                        ctx.data += "{0}{1} ".format(obj[key], units[key][1])
            else:
                ctx.data = str(cnt)
                if name in ("#HOW_MANY_TIMES", "#HOW_OFTEN"):
                    unit = _x.TextElement(units["times"][0])
                    ctx.data += " " + unit.make_agree_with_number(cnt).word
                    # Исправляем баг pymorphy со словом "раз"
                    if ctx.lang["LANG"] == "RU":
                        if 2 <= cnt % 10 <= 4 and (cnt < 10 or cnt > 20):
                            ctx.data += "а"
                if name == "#HOW_OFTEN":
                    keys = (units["hours"][0], units["days"][0])
                    ctx.data += "/"+_rnd.rnd_list(keys)
            return True
    return False

async def when(ctx: _ctx.ContextEx):
    if ctx.msg.items.has_phrases(ctx.lang["#WHEN"]):
        now = _app.Application.time()
        delta = random.randint(120, 2820) # 2-47 ч.
        for word in ctx.msg.items:
            # оч важно чтобы word было словом иначе вылет без указания ошибки
            if word.isalpha() and "past" in word.tag:
                delta = -delta
                break
        _when = now+datetime.timedelta(minutes=delta)
        ctx.data = "{0} {1} {2}:{3}".format(
            ctx.lang["TIME_OFFSET"][2+(_when.day-now.day)],
            ctx.lang["AT"],
            _when.hour,
            _when.minute
        )
        ctx.data = ctx.data[0].upper() + ctx.data[1:]
        return True
    return False

async def why(ctx: _ctx.ContextEx):
    return ctx.msg.items.has_phrases(ctx.lang["#WHY"])

async def which(ctx: _ctx.ContextEx):
    return ctx.lang["$WHICH"] in ctx.msg.items

async def whom(ctx: _ctx.ContextEx):
    return ctx.lang["$WHOM"] in ctx.msg.items

async def how(ctx: _ctx.ContextEx):
    return ctx.lang["$HOW"] in ctx.msg.items

async def any_q(ctx: _ctx.ContextEx):
    return ctx.msg.text and ctx.msg.text[-1] == '?'

# ======== ========= ========= ========= ========= ========= ========= =========

async def knock_0(ctx: _ctx.ContextEx):
    return ctx.msg.items.has_phrases(ctx.lang["#KNOCK"])

async def knock_any(ctx: _ctx.ContextEx):
    return ctx is not None

# ======== ========= ========= ========= ========= ========= ========= =========

async def vg_elo(ctx: _ctx.ContextEx, average=1200):
    if ctx.msg.items:
        if ctx.msg.items[0].lower in ctx.lang["$VG_ELO"] and len(ctx.msg.items) == 2:
            values = re.findall(r"\d+", ctx.msg.items[1].text)
            if len(values) == 2:
                values = (int(values[0]), int(values[1]))
                result = _vg.generate(values[0], values[1])
                if result:
                    if values[0] == 0 or values[1] == 0:
                        ctx.data = ", ".join([str(x) for x in result[0] or result[1]])
                    else:
                        ctx.data = "[Team 1]: " + ", ".join([str(x) for x in result[0]]) + '\n' + \
                                   "[Team 2]: " + ", ".join([str(x) for x in result[1]])
                else:
                    ctx.data = ctx.lang["=VG_ELO"]
            return True
    return False

# ======== ========= ========= ========= ========= ========= ========= =========
# Answer_key - ключи в json-файле, хранящем строки локализации
# Если перед именем стоит символ:
#   $ - Содержит список строк (слов), не требующих разбивание на слова
#   # - . . . . . . . . . . . . . . . . .требует разбить на слова
#   = - Категория ответов. Содержит список строк-ответов
# P.S.: Если идёт сразу текст, то это значит, что он не относится к командам

def _hello(ctx: _ctx.ContextEx):
    text = ctx.lang.rnd("=HELLO")
    if ctx.msgr.type_id == _msgr.TYPE_VK:
        if ctx.msg.from_id == 9752245:
            text = ctx.lang["$HELLO_9752245"]
    ctx.ans.set_text(text)

def _join(ctx: _ctx.ContextEx):
    ctx.ans.set_text("\n".join(ctx.data))

def _set(ctx: _ctx.ContextEx):
    ctx.ans.set_text(ctx.data)

def _where(ctx: _ctx.ContextEx):
    if type(ctx.data) is dict:
        ctx.ans.set_text(ctx.data["place"])
        ctx.ans.set_image(ctx.data["img"])
    else:
        ctx.ans.set_text(ctx.data)

def _who(ctx: _ctx.ContextEx):
    lst = ctx.lang["=WHO"]
    ctx.ans.set_text(_rnd.rnd_list(lst[0])+' '+_rnd.rnd_list(lst[1])+'?')

# ======== ========= ========= ========= ========= ========= ========= =========

def attach():
    #        condition  answer_key  cd  lim      access_type          name
    _cmd.new(hello,     _hello,     120, 0, _cmd.ACCESS_LOCK,         name="Hello",      appeal=False)
    _cmd.new(goodbye,   "=GOODBYE", 120, 0, _cmd.ACCESS_LOCK,         name="Goodbye",    appeal=False)
    _cmd.new(sleep,     "=SLEEP",   120, 0, _cmd.ACCESS_LOCK,         name="Sleep",      appeal=False)
    # Уникальные команды
    _cmd.new(calculate, _join,        0, 0, _cmd.ACCESS_PERSONAL,     name="Calculate")
    _cmd.new(acronym,   _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="Acronym")
    _cmd.new(date,      _set,       600, 1, _cmd.ACCESS_ALL_AT_ONCE,  name="Date")       # Перед HowMuch
    _cmd.new(hit,       _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="Hit")
    _cmd.new(is_true,   "=IS_TRUE",   0, 0, _cmd.ACCESS_PERSONAL,     name="IsTrue")
    _cmd.new(repeat,    _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="Repeat")
    _cmd.new(variants,  _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="Variants")   # Перед Who
    # Тук-тук -> Кто там? -> Сто грамм -> Очень смешно...
    _cmd.new(knock_0,   "=KNOCK",     0, 1, _cmd.ACCESS_PERSONAL, 20, name="KnockKnock", nodes=[
        _cmd.CommandNode(knock_any, "=KNOCK_ANY", 20, 0)
    ])
    # Специфическое
    _cmd.new(vg_elo,    _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="VaingloryELO")
    # Общие вопросы:
    _cmd.new(how_much,  _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="HowMuch")
    _cmd.new(where,     _where,       0, 0, _cmd.ACCESS_PERSONAL,     name="Where")
    _cmd.new(when,      _set,         0, 0, _cmd.ACCESS_PERSONAL,     name="When")
    _cmd.new(who,       _who,         0, 0, _cmd.ACCESS_PERSONAL,     name="Who")
    _cmd.new(which,     "=WHICH",     0, 0, _cmd.ACCESS_PERSONAL,     name="Which")
    _cmd.new(whom,      "=WHOM",      0, 0, _cmd.ACCESS_PERSONAL,     name="Whom")
    _cmd.new(why,       "=WHY",       0, 0, _cmd.ACCESS_PERSONAL,     name="Why")
    # DialogFlow
    _cmd.add(_dlg.DialogFlowCommand(name="DialogFlow"))
    # После HowMuch и DialogFlow
    _cmd.new(how,       "=HOW",       0, 0, _cmd.ACCESS_PERSONAL,     name="How")
    # Рандомный вопрос. Попытка ответить
    _cmd.new(any_q,    "=ANY_Q",      0, 0, _cmd.ACCESS_PERSONAL,     name="AnyQuestion")# После всех!

def dialogflow_init(configs):
    for cmd in _cmd.get_commands():
        if cmd.name == "DialogFlow":
            cmd.initialize(configs)
            break

# ======== ========= ========= ========= ========= ========= ========= =========
