# Используемые команды приложением
import core.messenger.messenger     as _msgr
import core.commands.command        as _cmd
import core.commands.context        as _ctx
import core.scripts.rand            as _rnd
import core.updater                 as _upd
import core.xlist                   as _x

import appx.cls.dialogflow_command  as _dlg
import appx.scripts.convert         as _conv
import appx.scripts.maps            as _maps
import appx.cls.calc                as _calc

import datetime
import aiohttp
import random

# ======== ========= ========= ========= ========= ========= ========= =========

async def hello(ctx: _ctx.ContextEx):
    return ctx.msg.items.contain(ctx.lang["$HELLO"])

async def goodbye(ctx: _ctx.ContextEx):
    if ctx.msg.items:
        return ctx.msg.items.has_phrases(ctx.lang["#GOODBYE"]) or \
               ctx.msg.items[0].lower in ctx.lang["$GOODBYE2"]
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
        time_offset = ctx.lang["TIME_OFFSET"]
        for word in ctx.msg.items:
            if word in time_offset:
                delta = time_offset.index(word)-2
                break
        now  = _upd.time()+datetime.timedelta(days=delta)
        plus = '+'*(_upd.G_TIMEZONE >= 0)
        ctx.data = now.strftime("%d/%m/%Y %H:%M")
        ctx.data += " (UTC {0}{1}:00)".format(plus, _upd.G_TIMEZONE)
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
            end = _list.find(_or, start, index=True)
            parts += [ctx.msg.items.get(start, end or len(_list))]
            if end is None:
                break
            start = end+1
        if parts:
            ctx.data = _rnd.rnd_list(parts)
            if ctx.data in ctx.lang["CATHERINE"] or ctx.lang["$ME"] in ctx.data:
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
    if ctx.lang["$WHERE"] in ctx.msg.items:
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
        now = _upd.time()
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
        print(ctx.data)
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
    _cmd.new(hello,     _hello,     300, 0, _cmd.ACCESS_PERSONAL,     name="Hello",      appeal=False)
    _cmd.new(goodbye,   "=GOODBYE", 300, 0, _cmd.ACCESS_PERSONAL,     name="Goodbye",    appeal=False)
    _cmd.new(sleep,     "=SLEEP",   300, 0, _cmd.ACCESS_PERSONAL,     name="Sleep",      appeal=False)
    # Уникальные команды
    _cmd.new(calculate, _join,        0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Calculate")
    _cmd.new(acronym,   _set,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Acronym")
    _cmd.new(date,      _set,       600, 1, _cmd.ACCESS_ALL_AT_ONCE,  name="Date")       # Перед HowMuch
    _cmd.new(hit,       _set,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Hit")
    _cmd.new(is_true,   "=IS_TRUE",   0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="IsTrue")
    _cmd.new(repeat,    _set,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Repeat")
    _cmd.new(variants,  _set,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Variants")   # Перед Who
    # Тук-тук -> Кто там? -> Сто грамм -> Очень смешно...
    _cmd.new(knock_0,   "=KNOCK",     0, 1, _cmd.ACCESS_PERSONAL, 20, name="KnockKnock", nodes=[
        _cmd.CommandNode(knock_any, "=KNOCK_ANY", 20, 0)
    ])
    # DialogFlow
    _cmd.add(_dlg.DialogFlowCommand(name="DialogFlow"))
    # Общие вопросы:
    _cmd.new(how_much,  _set,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="HowMuch")
    _cmd.new(where,     _where,       0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Where")
    _cmd.new(when,      _set,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="When")
    _cmd.new(who,       _who,         0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Who")

    _cmd.new(which,     "=WHICH",     0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Which")
    _cmd.new(whom,      "=WHOM",      0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Whom")
    _cmd.new(how,       "=HOW",       0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="How")        # После HowMuch
    _cmd.new(why,       "=WHY",       0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="Why")
    # Рандомный вопрос. Попытка ответить
    _cmd.new(any_q,    "=ANY_Q",      0, 0, _cmd.ACCESS_ALL_AT_ONCE,  name="AnyQuestion")# После всех!

def dialogflow_init(configs):
    for cmd in _cmd.get_commands():
        if cmd.name == "DialogFlow":
            cmd.initialize(configs)
            break

# ======== ========= ========= ========= ========= ========= ========= =========
