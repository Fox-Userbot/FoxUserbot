from pyrogram import Client
from modules.plugins_1system.restarter import restart
from command import *
import os
import configparser


PATH_FILE = "userdata/config.ini"

config = configparser.ConfigParser()
config.read(PATH_FILE)

@Client.on_message(fox_command("sp", "SetPrefix", os.path.basename(__file__), "[new prefix]") & fox_sudo())
async def sprefix(client, message):
    message = await who_message(client, message)
    prefixgett = message.command[1]
    config.set("prefix", "prefix", prefixgett)
    with open(PATH_FILE, "w") as config_file:
        config.write(config_file)
    await message.edit(f"<emoji id='5237699328843200968'>✅</emoji> <b>prefix [ <code>{prefixgett}</code> ] set!</b>\n<emoji id='5264727218734524899'>🔄</emoji> Restarting userbot...")
    await restart(message, restart_type="restart")


