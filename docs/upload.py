# 28.05.2022 Загружает локальные файлы на Яндекс.Диск
import yadisk
import json
import os

# ======== ========= ========= ========= ========= ========= ========= =========

api = None
data = None

# ======== ========= ========= ========= ========= ========= ========= =========

def upload_dir(src_path, dst_path):
    if not api.exists(dst_path):
        api.mkdir(dst_path)
    for name in os.listdir(src_path):
        if os.path.isdir(src_path + name):
            if name == "logs":
                continue
            upload_dir(src_path + name + '/', dst_path + name + '/')
        else:
            api.upload(src_path + name, dst_path + name, overwrite=True)
            print("READY: " + dst_path + name)

# ======== ========= ========= ========= ========= ========= ========= =========

# Загрузка данных
with open("../data.json", 'r') as f:
    data = json.loads(f.read())
# Инициализация
api = yadisk.YaDisk(token=data["token"])
if not api.check_token():
    raise Exception("Token isn't correct!")
# Загружаем все содержимое папки на Яндекс.Диск
upload_dir("../"+data["src"], data["dst"])
