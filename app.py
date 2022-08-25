# 28.05.2022 - 17.06.2022
from appx.builder import AppBuilder

# ======== ========= ========= ========= ========= ========= ========= =========
# Все папки и файлы в хранилище должны существовать!

def preset():
    builder = AppBuilder("_data.json", "appx/lang/ru.json")
    builder.use_yandex_storage()
    builder.use_dialogflow()
    builder.use_events()
    builder.use_debug()
    return builder.get()

app = preset()
app.run()

# ======== ========= ========= ========= ========= ========= ========= =========
