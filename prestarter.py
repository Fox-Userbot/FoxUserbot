from pyrogram import Client, filters
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
import asyncio
import json
from command import get_module_text

LANGUAGES = {
    "en": {
        "restart_success": "<emoji id='5237699328843200968'>✅</emoji> <code>Userbot succesfully Restarted</code>",
        "update_completed": "<emoji id='5237699328843200968'>✅</emoji> <code>Update process completed!</code>",
        "error_message": "<emoji id='5210952531676504517'>❌</emoji> Got error: {error}\n\n {text}"
    },
    "ru": {
        "restart_success": "<emoji id='5237699328843200968'>✅</emoji> <code>Юзербот успешно перезапущен</code>",
        "update_completed": "<emoji id='5237699328843200968'>✅</emoji> <code>Процесс обновления завершен!</code>",
        "error_message": "<emoji id='5210952531676504517'>❌</emoji> Произошла ошибка: {error}\n\n {text}"
    },
    "ua": {
        "restart_success": "<emoji id='5237699328843200968'>✅</emoji> <code>Юзербот успішно перезапущено</code>",
        "update_completed": "<emoji id='5237699328843200968'>✅</emoji> <code>Процес оновлення завершено!</code>",
        "error_message": "<emoji id='5210952531676504517'>❌</emoji> Сталася помилка: {error}\n\n {text}"
    }
}

def prestart(api_id, api_hash, device_mod):
    from pyrogram.client import Client
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    app = Client("my_account", api_id=api_id, api_hash=api_hash, device_model=device_mod)
    print("📝 Logging: Checking connection to Telegram")
    
    async def check_connection():
        await app.connect()
        print("📝 Logging: Connection successful")
        await app.disconnect()
        print("📝 Logging: Disconnection after checking")
    
    loop.run_until_complete(check_connection())
    with app:
        if len(sys.argv) >= 4:
            restart_type = sys.argv[3]
            thread_id = None
            if len(sys.argv) >= 5 and sys.argv[4] != "None":
                try:
                    thread_id = int(sys.argv[4])
                except ValueError:
                    thread_id = None
                    
            if restart_type == "1":
                text = get_module_text("update_completed", LANGUAGES)
            else:
                text = get_module_text("restart_success", LANGUAGES)
            try:
                try:
                    chat_id = int(sys.argv[1])
                except:
                    chat_id = str(sys.argv[1])
                if (str(chat_id).replace("@", "")) != "None":
                    app.send_message(chat_id, text, message_thread_id=thread_id)
            except Exception as f:
                da = get_module_text('error_message',LANGUAGES,error=f,text=text)
                app.send_message("me", da)
        
        # Triggers
        for i in os.listdir("triggers"):
            with open(f"triggers/{i}", 'r') as f:
                text = f.read().strip()
                app.send_message("me", text, schedule_date=(datetime.now() + timedelta(seconds=70)))

        # Sudo User
        current_user_id = (app.get_users("me")).id
        try:
            with open(Path("userdata/sudo_users.json"), "r") as f:
                existing_users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_users = []
        if current_user_id not in existing_users:
            existing_users.append(current_user_id)
            with open(Path("userdata/sudo_users.json"), "w") as f:
                json.dump(existing_users, f)

