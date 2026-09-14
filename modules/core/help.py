# -*- coding: utf-8 -*-
import configparser
import html
import os
import random
from pathlib import Path

from pyrogram import Client
from telegraph import Telegraph

from command import fox_command, fox_sudo, who_message, get_text, my_prefix
from modules.core.settings.main_settings import module_list, version

# Default
DEFAULT_HELP_IMAGE = "https://raw.githubusercontent.com/Fox-Userbot/FoxUserbot/main/photos/FoxUB_help.jpg"
THEME_PATH = "userdata/theme.ini"
CACHE_DIR = "temp"
CACHE_CONTENT_FILE = os.path.join(CACHE_DIR, "help_content.txt")
CACHE_LINK_FILE = os.path.join(CACHE_DIR, "help_link.txt")

LANGUAGES = {
    "en": {
        "loading": "Loading the help menu...",
        "commands_list": "⬆️ | List of all commands.",
        "default_text": """
<emoji id="5190875290439525089">🦊</emoji><b> | FoxUserbot RUNNING</b>
<emoji id="5197288647275071607">🔒</emoji><b> | Version: </b><b>{version}</b>
<emoji id="5193177581888755275">💼</emoji><b> | Modules: {modules_count}</b>
<emoji id="5444856076954520455">🔒</emoji><b> | Prefix: {prefix}</b>
<emoji id="5436113877181941026">❓</emoji><a href="{commands_link}"><b> | List of all commands. </b></a>
"""
    },
    "ru": {
        "loading": "Загрузка меню помощи...",
        "commands_list": "⬆️ | Список всех команд.",
        "default_text": """
<emoji id="5190875290439525089">🦊</emoji><b> | FoxUserbot ЗАПУЩЕН</b>
<emoji id="5197288647275071607">🔒</emoji><b> | Версия: </b><b>{version}</b>
<emoji id="5193177581888755275">💼</emoji><b> | Модули: {modules_count}</b>
<emoji id="5444856076954520455">🔒</emoji><b> | Префикс: {prefix}</b>
<emoji id="5436113877181941026">❓</emoji><a href="{commands_link}"><b> | Список всех команд. </b></a>
"""
    },
    "ua": {
        "loading": "Завантаження меню допомоги...",
        "commands_list": "⬆️ | Список усіх команд.",
        "default_text": """
<emoji id="5190875290439525089">🦊</emoji><b> | FoxUserbot ЗАПУЩЕНИЙ</b>
<emoji id="5197288647275071607">🔒</emoji><b> | Версія: </b><b>{version}</b>
<emoji id="5193177581888755275">💼</emoji><b> | Модулі: {modules_count}</b>
<emoji id="5444856076954520455">🔒</emoji><b> | Префікс: {prefix}</b>
<emoji id="5436113877181941026">❓</emoji><a href="{commands_link}"><b> | Список усіх команд. </b></a>
"""
    }
}

def get_help_image():
    if not Path(THEME_PATH).exists():
        return DEFAULT_HELP_IMAGE

    try:
        config = configparser.ConfigParser()
        config.read(THEME_PATH, encoding='utf-8')
        return config.get("help", "image", fallback=DEFAULT_HELP_IMAGE)
    except:
        return DEFAULT_HELP_IMAGE

def get_modules_content():
    content = []
    for module_name, commands in module_list.items():
        if isinstance(commands, list):
            commands = " | ".join(commands)
        content.append(f"{module_name}:{commands}")
    return "\n".join(content)

def get_cached_telegraph_link():
    if os.path.exists(CACHE_LINK_FILE) and os.path.exists(CACHE_CONTENT_FILE):
        try:
            with open(CACHE_CONTENT_FILE, 'r', encoding='utf-8') as f:
                cached_content = f.read().strip()
            
            current_content = get_modules_content()
            
            if cached_content == current_content:
                with open(CACHE_LINK_FILE, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except:
            pass
    return None

def cache_telegraph_link(link):
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    try:
        current_content = get_modules_content()
        with open(CACHE_CONTENT_FILE, 'w', encoding='utf-8') as f:
            f.write(current_content)
        with open(CACHE_LINK_FILE, 'w', encoding='utf-8') as f:
            f.write(link)
    except Exception as e:
        print(f"Error caching telegraph link: {e}")

def create_html_file(content):
    os.makedirs(CACHE_DIR, exist_ok=True)
    file_name = f"help_{random.randint(10000, 99999)}.html"
    file_path = os.path.join(CACHE_DIR, file_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FoxUserbot Help</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .module {{ margin-bottom: 20px; }}
        .command {{ margin-left: 20px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>FoxUserbot Help</h1>
    {content}
</body>
</html>""")
    
    return file_path

def get_help_text():
    cached_link = get_cached_telegraph_link()
    
    lists = []
    for module_name, commands in module_list.items():
        text = ""
        if isinstance(commands, list):
            for i in commands:
                text += f"{i} | "
            text = text[:-2]
            commands = text
        command_list = [cmd.strip() for cmd in commands.split("|")]

        escaped_module_name = html.escape(str(module_name), quote=True)
        escaped_commands = [html.escape(str(cmd), quote=True) for cmd in command_list]
        module_block = [
            f"➣ Module <b>[{escaped_module_name}]</b>",
            *[f"Command: <code>{cmd}</code>" for cmd in escaped_commands],
            "" 
        ]
        lists.extend(module_block)

    a = "<br>".join(lists)
    
    html_file_path = None
    
    if cached_link:
        link = cached_link
    else:
        try:
            telegraph = Telegraph()
            telegraph.create_account(short_name='FoxServices')
            page = telegraph.create_page(
                f'FoxUserbot Help {random.randint(10000, 99999)}', 
                html_content=a
            )
            link = f"https://telegra.ph/{page['path']}"
            cache_telegraph_link(link)
        except Exception as e:
            html_file_path = create_html_file(a)
            link = "https://telegra.ph/"
    
    custom_text = None
    if Path(THEME_PATH).exists():
        try:
            config = configparser.ConfigParser()
            config.read(THEME_PATH, encoding='utf-8')
            custom_text = config.get("help", "text", fallback=None)
            if custom_text and custom_text.strip() and custom_text != "Not set":
                aliases = {
                    '{version}': version,
                    '{modules_count}': str(len(module_list)),
                    '{prefix}': my_prefix(),
                    '{commands_link}': link,
                }
                for alias, value in aliases.items():
                    custom_text = custom_text.replace(alias, str(value))
                return custom_text, html_file_path
        except Exception as e:
            pass
    
    default_text = get_text("help", "default_text", LANGUAGES=LANGUAGES)
    text = default_text.format(
        version=version,
        modules_count=len(module_list),
        prefix=my_prefix(),
        commands_link=link
    )
    return text, html_file_path

@Client.on_message(fox_command("help", "Help", os.path.basename(__file__)) & fox_sudo())
async def helps(client, message):
    message = await who_message(client, message)
    html_file_path = None
    try:
        image_url = get_help_image()
        loading_text = get_text("help", "loading", LANGUAGES=LANGUAGES)
        
        if image_url.split(".")[-1].lower() in ["mp4", "mov", "avi", "mkv", "webm"]:
            da = await client.send_video(
                message.chat.id, 
                video=image_url, 
                caption=loading_text, 
                message_thread_id=message.message_thread_id
            )

        elif image_url.split(".")[-1].lower() == "gif":
            da = await client.send_animation(
                message.chat.id, 
                animation=image_url, 
                caption=loading_text, 
                message_thread_id=message.message_thread_id
            )
        else:
            da = await client.send_photo(
            message.chat.id, 
            photo=image_url, 
            caption=loading_text, 
            message_thread_id=message.message_thread_id 
        )
        await message.delete()
        caption, html_file_path = get_help_text()
        await client.edit_message_caption(message.chat.id, da.id, caption)
        
        if html_file_path:
            commands_list_text = get_text("help", "commands_list", LANGUAGES=LANGUAGES)
            await client.send_document(
                message.chat.id,
                document=html_file_path,
                caption=commands_list_text,
                message_thread_id=message.message_thread_id
            )
            os.remove(html_file_path)
            
    except Exception as e:
        try:
            da = await client.send_photo(
                message.chat.id, 
                photo=DEFAULT_HELP_IMAGE, 
                caption=loading_text, 
                message_thread_id=message.message_thread_id
            )
            await message.delete()
            caption, html_file_path = get_help_text()
            await client.edit_message_caption(message.chat.id, da.id, caption)
            
            if html_file_path:
                commands_list_text = get_text("help", "commands_list", LANGUAGES=LANGUAGES)
                await client.send_document(
                    message.chat.id,
                    document=html_file_path,
                    caption=commands_list_text,
                    message_thread_id=message.message_thread_id
                )
                os.remove(html_file_path)
                
        except:
            try:
                da = await client.send_photo(
                    message.chat.id, 
                    photo="photos/FoxUB_help.jpg", 
                    caption=loading_text, 
                    message_thread_id=message.message_thread_id
                )
                await message.delete()
                caption, html_file_path = get_help_text()
                await client.edit_message_caption(message.chat.id, da.id, caption)
                
                if html_file_path:
                    commands_list_text = get_text("help", "commands_list", LANGUAGES=LANGUAGES)
                    await client.send_document(
                        message.chat.id,
                        document=html_file_path,
                        caption=commands_list_text,
                        message_thread_id=message.message_thread_id
                    )
                    os.remove(html_file_path)
                    
            except:
                await message.edit(loading_text)
                caption, html_file_path = get_help_text()
                await message.edit(caption)
                
                if html_file_path:
                    commands_list_text = get_text("help", "commands_list", LANGUAGES=LANGUAGES)
                    await client.send_document(
                        message.chat.id,
                        document=html_file_path,
                        caption=commands_list_text,
                        message_thread_id=message.message_thread_id
                    )
                    os.remove(html_file_path)