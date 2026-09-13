# -*- coding: utf-8 -*-
import os
import shutil
import traceback
import zipfile
from datetime import date

import wget
from pyrogram import Client
from pyrogram.types import Message

from command import fox_command, fox_sudo, who_message, get_text

filename = os.path.basename(__file__)
Module_Name = 'Restarter'

LANGUAGES = {
    "en": {
        "updating": "<emoji id='5264727218734524899'>🔄</emoji> **Updating {repo_type}...**",
        "update_success": "<emoji id='5237699328843200968'>✅</emoji> **Userbot successfully updated\n<emoji id='5264727218734524899'>🔄</emoji> Restarting...**",
        "error_occurred": "<emoji id='5210952531676504517'>❌</emoji> **An error occurred:**\n\n`{error}`",
        "restarting": "<emoji id='5264727218734524899'>🔄</emoji> **Restarting userbot...**",
        "restart_error": "<emoji id='5210952531676504517'>❌</emoji> **An error occurred...**"
    },
    "ru": {
        "updating": "<emoji id='5264727218734524899'>🔄</emoji> **Обновление {repo_type}...**",
        "update_success": "<emoji id='5237699328843200968'>✅</emoji> **Юзербот успешно обновлен\n<emoji id='5264727218734524899'>🔄</emoji> Перезапуск...**",
        "error_occurred": "<emoji id='5210952531676504517'>❌</emoji> **Произошла ошибка:**\n\n`{error}`",
        "restarting": "<emoji id='5264727218734524899'>🔄</emoji> **Перезапуск юзербота...**",
        "restart_error": "<emoji id='5210952531676504517'>❌</emoji> **Произошла ошибка...**"
    },
    "ua": {
        "updating": "<emoji id='5264727218734524899'>🔄</emoji> **Оновлення {repo_type}...**",
        "update_success": "<emoji id='5237699328843200968'>✅</emoji> **Юзербот успішно оновлено\n<emoji id='5264727218734524899'>🔄</emoji> Перезавантаження...**",
        "error_occurred": "<emoji id='5210952531676504517'>❌</emoji> **Сталася помилка:**\n\n`{error}`",
        "restarting": "<emoji id='5264727218734524899'>🔄</emoji> **Перезапуск юзербота...**",
        "restart_error": "<emoji id='5210952531676504517'>❌</emoji> **Сталася помилка...**"
    }
}


# Update mirrors: tried in order until one downloads. Full archive URLs on purpose —
# every git host has its own format (GitHub: .../archive/refs/heads/main.zip,
# Forgejo: .../archive/main.zip), so mirrors store ready links, not a template.
# "expires" is the last valid day (YYYY-MM-DD); expired mirrors are skipped.
# Add new mirrors here as {"main": "https://...", "beta": "https://...", "expires": "YYYY-MM-DD"}.
UPDATE_MIRRORS = [
    {
        "main": "https://rpi4b.tailb2d7b7.ts.net/FoxUserbot/FoxUserbot/archive/main.zip",
        "beta": "https://rpi4b.tailb2d7b7.ts.net/FoxUserbot/FoxUserbot-dev/archive/main.zip",
        "expires": "2026-11-13",
    },
    {
        "main": "https://git.a9fm.best/FoxUserbot/FoxUserbot/archive/main.zip",
        "beta": "https://git.a9fm.best/FoxUserbot/FoxUserbot-dev/archive/main.zip",
        "expires": "2027-02-20",
    },
]



def restart_executor(chat_id=None, message_id=None, text=None, thread=None):
    if os.name == "nt":
        os.execvp(
            "python",
            [
                "python",
                "main.py",
                f"{chat_id}",
                f"{message_id}",
                f"{text}",
                f"{thread}" if thread else "None",
            ],
        )
    else:
        os.execvp(
            "python3",
            [
                "python3",
                "main.py",
                f"{chat_id}",
                f"{message_id}",
                f"{text}",
                f"{thread}" if thread else "None",
            ],
        )


async def restart(message: Message, restart_type):
    if restart_type == "update":
        text = "1"
    else:
        text = "2"
    thread_id = message.message_thread_id if message.message_thread_id else None
    chat_id = message.chat.username if message.chat.username else message.chat.id
    restart_executor(chat_id, message.id, text, thread_id)


def download_from_mirrors(repo_type, dest):
    """Download repo_type ('main' or 'beta') archive from first working mirror. Return used URL."""
    today = date.today()
    errors = []
    for mirror in UPDATE_MIRRORS:
        url = mirror[repo_type]
        if today > date.fromisoformat(mirror["expires"]):
            errors.append(f"{url} (expired {mirror['expires']})")
            continue
        try:
            wget.download(url, dest)
            return url
        except Exception as e:
            errors.append(f"{url} ({e})")
            try:
                os.remove(dest)
            except OSError:
                pass
    raise Exception("All update mirrors failed: " + "; ".join(errors))


async def update_repository(client, message, repo_type):
    try:
        try:
            os.remove("temp/archive.zip")
        except:
            pass

        await message.edit(get_text("restarter", "updating", LANGUAGES=LANGUAGES, repo_type=repo_type))

        download_from_mirrors(repo_type, "temp/archive.zip")

        with zipfile.ZipFile("temp/archive.zip", "r") as zip_ref:
            file_list = zip_ref.namelist()
            root_folder = None
            for file in file_list:
                if file.endswith('/') and file.count('/') == 1:
                    root_folder = file.strip('/')
                    break
            
            if not root_folder:
                raise Exception("Not found root dir")

            zip_ref.extractall("temp/")

        os.remove("temp/archive.zip")
        shutil.make_archive("temp/archive", "zip", f"temp/{root_folder}/")
        with zipfile.ZipFile("temp/archive.zip", "r") as zip_ref:
            zip_ref.extractall(".")

        os.remove("temp/archive.zip")
        shutil.rmtree(f"temp/{root_folder}")
        
        await message.edit(get_text("restarter", "update_success", LANGUAGES=LANGUAGES))
        await restart(message, restart_type="update")
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        error_message = get_text("restarter", "error_occurred", LANGUAGES=LANGUAGES, error=str(e))

        if len(error_message) > 4000:
            error_message = error_message[:4000] + "..."
        
        await message.edit(error_message)


# Restart
@Client.on_message(fox_command("restart", Module_Name, filename) & fox_sudo())
async def restart_get(client, message):
    message = await who_message(client, message)
    try:
        await message.edit(get_text("restarter", "restarting", LANGUAGES=LANGUAGES))
        await restart(message, restart_type="restart")
    except:
        await message.edit(get_text("restarter", "restart_error", LANGUAGES=LANGUAGES))


# Update main
@Client.on_message(fox_command("update", Module_Name, filename) & fox_sudo())
async def update(client, message):
    message = await who_message(client, message)
    await update_repository(client, message, "main")


# Update beta
@Client.on_message(fox_command("beta", Module_Name, filename) & fox_sudo())
async def update_beta(client, message):
    message = await who_message(client, message)

    await update_repository(client, message, "beta")
