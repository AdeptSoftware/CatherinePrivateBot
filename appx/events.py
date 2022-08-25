#
from core.updater 	import timezone
from core.event		import Event
import datetime

# ======== ========= ========= ========= ========= ========= ========= =========
# Типы событий

TYPE_TIMETABLE = 0					# Вывод текста по расписанию

# ======== ========= ========= ========= ========= ========= ========= =========

def timetable(event: Event):
	""" Определяет время вывода событий и управляет их выводом

	:param event: Текущее событие
	:return: Всегда возвращает True, что запрещает EventManager'у удалять это
		событие из очереди
	"""
	data = event.data
	if event.reserve:
		ans = data["msgr"].create_answer(data["pid"])
		ans.set_text(event.reserve)
		data["msgr"].send(ans.get())
		event.reserve = None
	# Определение времени отправки следующего сообщения (z)
	days = 0
	offset = data["timezone"]-timezone()
	now = datetime.datetime.now() + datetime.timedelta(hours=offset)
	while days < 8:			# Неделя+1
		for msg in data["lst"]:
			z = datetime.datetime(now.year, now.month, now.day, msg["hour"], msg["minute"])
			z += datetime.timedelta(days=days)
			if msg["isoweekday"] is None or z.isoweekday() in msg["isoweekday"]:
				if now > z:
					continue
				event.reserve = msg["params"]
				cooldown = (z-now).total_seconds()
				if cooldown < 0:
					cooldown = 5
				event.cooldown = cooldown
				return True
		days += 1
	return True

# ======== ========= ========= ========= ========= ========= ========= =========

def loader(app, filename="events.json"):
	""" Загрузчик событий из json-файла

	:param app: :class:`core.commands.context.CommonData`
	:param filename: откуда загружаем события
	"""
	data = app.storage.create_storage_object(filename).get()
	with data:
		for event in data.value:
			if event["type"] == TYPE_TIMETABLE:
				event["data"]["msgr"] = app.messengers[event["msgr_id"]]
				app.events.new(timetable, event)

# ======== ========= ========= ========= ========= ========= ========= =========
