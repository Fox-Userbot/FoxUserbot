# -*- coding: utf-8 -*-
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from pyrogram import Client

from command import fox_command, fox_sudo, who_message, get_text
from modules.core.restarter import restart
from modules.core.settings.main_settings import version

# backup_dirs
BACKUP_PATHS = [
    'userdata',
    'triggers', 
    'modules/loaded'
]

LANGUAGES = {
    "en": {
        "need_reply": "<b><emoji id='5210952531676504517'>❌</emoji> Need to reply to a message with a backup archive!</b>",
        "invalid_archive": "<b><emoji id='5210952531676504517'>❌</emoji> Invalid backup archive!</b>",
        "restored": "<b><emoji id='5237699328843200968'>✅</emoji> Data restored successfully!</b>",
        "restore_error": "<b><emoji id='5210952531676504517'>❌</emoji> Restore Error:</b>\n<code>{error}</code>",
        "creating": "<b><emoji id='5264727218734524899'>🔄</emoji> Creating a backup copy...</b>",
        "empty_file": "<b><emoji id='5210952531676504517'>❌</emoji> Error creating backup:</b>\n<code>Backup file is empty</code>",
        "backup_error": "<b><emoji id='5210952531676504517'>❌</emoji> Error creating backup:</b>\n<code>{error}</code>",
        "ready_restore": "<b><emoji id='5264727218734524899'>🔄</emoji> Ready for restoration...</b>",
        "creating_modules": "<b><emoji id='5264727218734524899'>🔄</emoji> Creating modules backup...</b>",
        "modules_error": "<b><emoji id='5210952531676504517'>❌</emoji> Error creating modules backup:</b>\n<code>{error}</code>",
        "caption": """<emoji id='5472308992514464048'>🔐</emoji> | Backup {filename}
<emoji id='5283051451889756068'>🦊</emoji> | Only for FoxUserbot
<emoji id='5296369303661067030'>🔒</emoji> | Version: {version}
<emoji id='5271604874419647061'>🔗</emoji> | https://github.com/Fox-Userbot/FoxUserbot"""
    },
    "ru": {
        "need_reply": "<b><emoji id='5210952531676504517'>❌</emoji> Нужно ответить на сообщение с архивом бэкапа!</b>",
        "invalid_archive": "<b><emoji id='5210952531676504517'>❌</emoji> Неверный архив бэкапа!</b>",
        "restored": "<b><emoji id='5237699328843200968'>✅</emoji> Данные успешно восстановлены!</b>",
        "restore_error": "<b><emoji id='5210952531676504517'>❌</emoji> Ошибка восстановления:</b>\n<code>{error}</code>",
        "creating": "<b><emoji id='5264727218734524899'>🔄</emoji> Создание резервной копии...</b>",
        "empty_file": "<b><emoji id='5210952531676504517'>❌</emoji> Ошибка создания бэкапа:</b>\n<code>Файл бэкапа пуст</code>",
        "backup_error": "<b><emoji id='5210952531676504517'>❌</emoji> Ошибка создания бэкапа:</b>\n<code>{error}</code>",
        "ready_restore": "<b><emoji id='5264727218734524899'>🔄</emoji> Готов к восстановлению...</b>",
        "creating_modules": "<b><emoji id='5264727218734524899'>🔄</emoji> Создание бэкапа модулей...</b>",
        "modules_error": "<b><emoji id='5210952531676504517'>❌</emoji> Ошибка создания бэкапа модулей:</b>\n<code>{error}</code>",
        "caption": """<emoji id='5472308992514464048'>🔐</emoji> | Бэкап {filename}
<emoji id='5283051451889756068'>🦊</emoji> | Только для FoxUserbot
<emoji id='5296369303661067030'>🔒</emoji> | Версия: {version}
<emoji id='5271604874419647061'>🔗</emoji> | https://github.com/Fox-Userbot/FoxUserbot"""
    },
    "ua": {
        "need_reply": "<b><emoji id='5210952531676504517'>❌</emoji> Потрібно відповісти на повідомлення з архівом бекапу!</b>",
        "invalid_archive": "<b><emoji id='5210952531676504517'>❌</emoji> Невірний архів бекапу!</b>",
        "restored": "<b><emoji id='5237699328843200968'>✅</emoji> Дані успішно відновлено!</b>",
        "restore_error": "<b><emoji id='5210952531676504517'>❌</emoji> Помилка відновлення:</b>\n<code>{error}</code>",
        "creating": "<b><emoji id='5264727218734524899'>🔄</emoji> Створення резервної копії...</b>",
        "empty_file": "<b><emoji id='5210952531676504517'>❌</emoji> Помилка створення бекапу:</b>\n<code>Файл бекапу порожній</code>",
        "backup_error": "<b><emoji id='5210952531676504517'>❌</emoji> Помилка створення бекапу:</b>\n<code>{error}</code>",
        "ready_restore": "<b><emoji id='5264727218734524899'>🔄</emoji> Готовий до відновлення...</b>",
        "creating_modules": "<b><emoji id='5264727218734524899'>🔄</emoji> Створення бекапу модулів...</b>",
        "modules_error": "<b><emoji id='5210952531676504517'>❌</emoji> Помилка створення бекапу модулів:</b>\n<code>{error}</code>",
        "caption": """<emoji id='5472308992514464048'>🔐</emoji> | Бекап {filename}
<emoji id='5283051451889756068'>🦊</emoji> | Тільки для FoxUserbot
<emoji id='5296369303661067030'>🔒</emoji> | Версія: {version}
<emoji id='5271604874419647061'>🔗</emoji> | https://github.com/Fox-Userbot/FoxUserbot"""
    }
}

async def create_backup() -> str:
    def exclude_sudo_users(tarinfo):
        if tarinfo.name == "userdata/sudo_users.json":
            return None
        return tarinfo

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with tempfile.NamedTemporaryFile(suffix=f'_FoxUB_Backup_{timestamp}.tar.gz', delete=False) as tmp:
        with tarfile.open(tmp.name, mode='w:gz') as tar:
            for path in BACKUP_PATHS:
                if os.path.exists(path):
                    tar.add(path, filter=exclude_sudo_users)
        return tmp.name

async def restore_backup(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        need_reply_text = get_text("backup", "need_reply", LANGUAGES=LANGUAGES)
        await message.edit(need_reply_text)
        return False

    try:
        download_path = await message.reply_to_message.download()
        
        try:
            with tarfile.open(download_path, 'r:gz') as test_tar:
                test_tar.getmembers()
        except:
            invalid_text = get_text("backup", "invalid_archive", LANGUAGES=LANGUAGES)
            await message.edit(invalid_text)
            return False
        
        for path in BACKUP_PATHS:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

        with tarfile.open(download_path, 'r:gz') as tar:
            tar.extractall()
        
        restored_text = get_text("backup", "restored", LANGUAGES=LANGUAGES)
        await message.edit(restored_text)
        return True
        
    except Exception as e:
        error_text = get_text("backup", "restore_error", LANGUAGES=LANGUAGES, error=str(e))
        await message.edit(error_text)
        return False
    finally:
        if 'download_path' in locals() and os.path.exists(download_path):
            os.remove(download_path)

@Client.on_message(fox_command("backup", "Backup", os.path.basename(__file__)) & fox_sudo())
async def backup_command(client, message):
    message = await who_message(client, message)
    backup_file = None
    try:
        creating_text = get_text("backup", "creating", LANGUAGES=LANGUAGES)
        msg = await message.edit(creating_text)
        backup_file = await create_backup()
        
        if os.path.getsize(backup_file) == 0:
            empty_text = get_text("backup", "empty_file", LANGUAGES=LANGUAGES)
            await message.edit(empty_text)
            return
        
        caption_text = get_text("backup", "caption", LANGUAGES=LANGUAGES, 
                               filename=Path(backup_file).name, version=version)
        
        await client.send_document(
            chat_id=message.chat.id,
            document=backup_file,
            caption=caption_text,
            message_thread_id=message.message_thread_id
        )
        await msg.delete()
        
    except Exception as e:
        error_text = get_text("backup", "backup_error", LANGUAGES=LANGUAGES, error=str(e))
        await message.edit(error_text)
        
    finally:
        if backup_file and os.path.exists(backup_file):
            os.remove(backup_file)

@Client.on_message(fox_command("restore", "Backup", os.path.basename(__file__), "[reply]") & fox_sudo())
async def restore_command(client, message):
    message = await who_message(client, message)
    try:
        ready_text = get_text("backup", "ready_restore", LANGUAGES=LANGUAGES)
        await message.edit(ready_text)
        success = await restore_backup(client, message)
        if success:
            await restart(message, restart_type="restart")
    except Exception as e:
        error_text = get_text("backup", "restore_error", LANGUAGES=LANGUAGES, error=str(e))
        await message.edit(error_text)

@Client.on_message(fox_command("backup_modules", "Backup", os.path.basename(__file__)) & fox_sudo())
async def backup_modules_command(client, message):
    message = await who_message(client, message)
    backup_file = None
    try:
        creating_text = get_text("backup", "creating_modules", LANGUAGES=LANGUAGES)
        msg = await message.edit(creating_text)
        
        with tempfile.NamedTemporaryFile(suffix='_FoxUB_Modules_Backup.tar.gz', delete=False) as tmp:
            with tarfile.open(tmp.name, mode='w:gz') as tar:
                if os.path.exists('modules/loaded'):
                    tar.add('modules/loaded')
            backup_file = tmp.name
        
        if os.path.getsize(backup_file) == 0:
            empty_text = get_text("backup", "empty_file", LANGUAGES=LANGUAGES)
            await message.edit(empty_text)
            return
        
        caption_text = get_text("backup", "caption", LANGUAGES=LANGUAGES,
                               filename=Path(backup_file).name, version=version)
        
        await client.send_document(
            chat_id=message.chat.id,
            document=backup_file,
            caption=caption_text,
            message_thread_id=message.message_thread_id
        )
        await msg.delete()
        
    except Exception as e:
        error_text = get_text("backup", "modules_error", LANGUAGES=LANGUAGES, error=str(e))
        await message.edit(error_text)
        
    finally:
        if backup_file and os.path.exists(backup_file):
            os.remove(backup_file)