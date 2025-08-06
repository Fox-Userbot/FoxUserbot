from pyrogram import Client
from command import *
import os
from time import perf_counter


@Client.on_message(fox_command("ping", "Ping", os.path.basename(__file__)) & fox_sudo())
async def ping(client, message):
    message = await who_message(client, message)
    start = perf_counter()
    await message.edit("🏓| ⚾=== |🏓")
    await message.edit("🏓| =⚾== |🏓")
    await message.edit("🏓| ==⚾= |🏓")
    await message.edit("🏓| ===⚾ |🏓")
    end = perf_counter()

    pinges = ((end - start) / 4)
    ping = pinges * 1000

    if 0 <= ping <= 199:
        connect = "<emoji id='5416081784641168838'>🟢</emoji> Stable"
    if 199 <= ping <= 400:
        connect = "🟠 Good"
    if 400 <= ping <= 600:
        connect = "<emoji id='5411225014148014586'>🔴</emoji> Unstable"
    if 600 <= ping:
        connect = "⚠ Check you network connection"
    await message.edit(f"<b><emoji id='5269563867305879894'>🏓</emoji> Pong\n<emoji id='5783105032350076195'>📶</emoji></b> {round(ping)} ms\n{connect}")
