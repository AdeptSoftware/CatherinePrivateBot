#
import asyncio
import aiohttp
import random
import json
import re

# ======== ========= ========= ========= ========= ========= ========= =========

# _place = re.compile("<meta content=\"([^\"]+?)\" itemprop=\"description\">")
_json = re.compile(r"\[\"[\d\-°'.]+\\\"N [\d\-°'.]+\\\"E.+(?<=]])")

# ======== ========= ========= ========= ========= ========= ========= =========

#      51.1298611                 51°07'47.5
# Decimal Degrees (DD) -> Degrees Minutes Seconds (DMS)
def dd2dms(dd):
    d = int(dd)
    m = int((dd-d)*60)
    s = (dd-d-m/60)*3600
    return "{0}°{1}'{2:.1f}".format(d, m, s)

async def place(latitude, longitude):
    lat = dd2dms(latitude)
    lng = dd2dms(longitude)
    url = "https://www.google.com/maps/place/{0}\"N+{1}\"E/@{2:.7f},{3:.7f},17z?hl=ru"
    url = url.format(lat, lng, latitude, longitude)

    await asyncio.sleep(1)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            if not res.ok:
                return {"status_code": res.status}
            content = await res.text('utf-8')
    lst = _json.findall(content)
    if lst:
        data = json.loads(lst[0])
        return {
            "lat":   lat,
            "lng":   lng,
            "url":   url,
            "place": str(data[1]),
            "img":   data[2],
            "sz":    data[3]
        }

def rnd_pos(_min, _max):
    return (random.random()*(_max-_min))+_min

async def rnd_place():
    return await place(rnd_pos(15, 70), rnd_pos(10, 140))         # Большая часть суши Евразии
    # return await place(rnd_pos(-56, 77), rnd_pos(-180, 179))    # Почти весь мир

# ======== ========= ========= ========= ========= ========= ========= =========
