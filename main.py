"""
Сделать сервис генерации короткой ссылки
На fastapi или aiohttp сделать API с 3 эндпоинтами:
- Создание короткой ссылки (на вход передаём полный url, в ответ получаем короткий url)
- Удаление ссылки (на вход ранее сгенерированный короткий url, ответ статус операции)
- Получение полного url (на вход короткий url, в ответ полный url)

Пример полного url - https://music.yandex.ru/album/5307396/track/38633706
Пример короткого url - const.com/A8z1
БД - PostgreSQL (желательно) или SQLite
Код должна быть возможность запустить локально или в докере, как удобнее
"""

from fastapi import FastAPI
from datetime import datetime, timezone
import hashlib
import base64
from pydantic import BaseModel

from db import database, links
import conf


app = FastAPI()


class Link(BaseModel):
    url: str


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/short")
async def add_link(link: Link):
    """
    Создание короткой ссылки (на вход передаём полный url, в ответ получаем короткий url)
    """
    def create_short_link():
        to_encode = f'{link.url}{timestamp}'

        b64_encoded_str = base64.urlsafe_b64encode(
            hashlib.sha256(to_encode.encode()).digest()).decode()
        return b64_encoded_str[:7]

    timestamp = datetime.now().replace(tzinfo=timezone.utc).timestamp()
    short_link = f"{conf.URL}/{create_short_link()}"
    query = links.insert().values(url=link.url, short=short_link)
    await database.execute(query)
    return {"short": short_link}


@app.get("/")
async def get_short(short: str):
    """
    Получение полного url (на вход короткий url, в ответ полный url)
    """
    query = links.select().filter_by(short=short)
    link = await database.fetch_one(query)
    return link.url


@app.delete("/")
async def delete_link(link: Link):
    """
    Удаление ссылки (на вход ранее сгенерированный короткий url, ответ статус операции)
    """
    query = links.delete().where(links.c.short == link.url)
    res = await database.execute(query)
    if res:
        return {"status": "ok"}
    return {"status": "nothing to delete"}
