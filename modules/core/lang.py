# -*- coding: utf-8 -*-
import configparser
import os
from pathlib import Path

from pyrogram import Client

from command import all_lang, fox_command, fox_sudo, my_prefix, who_message, set_global_lang, get_global_lang , get_text

filename = os.path.basename(__file__)
Module_Name = 'Language'

LANGUAGES = {
    "en": {
        "success": "<emoji id=5202021044105257611>🇺🇸</emoji> Language set to: {lang}",
        "error": "❌ Error setting language", 
        "invalid": "❌ Invalid language! Available: {langs}",
        "usage": "🌐 Available languages: {langs}\n💡 Usage: <code>{my_prefix}setlang en</code>",
        "set_lang" : """
<emoji id=5447410659077661506>🌐</emoji> | <b>Current language:</b> {current_lang}
<emoji id=5395444784611480792>🔧</emoji> | <b>Global lang:</b> {global_lang}
<emoji id=5422439311196834318>💡</emoji> | <b>Available:</b> {available_langs}
        """
     },
    "ru": {
        "success": "<emoji id=5449408995691341691>🇷🇺</emoji> Язык установлен: {lang}",
        "error": "❌ Ошибка установки языка",
        "invalid": "❌ Неверный язык! Доступно: {langs}",
        "usage": "🌐 Доступные языки: {langs}\n💡 Использование: <code>{my_prefix}setlang en</code>",
        "set_lang" : """
<emoji id=5447410659077661506>🌐</emoji> | <b>Текущий язык:</b> {current_lang}
<emoji id=5395444784611480792>🔧</emoji> | <b>Глобальный язык:</b> {global_lang}
<emoji id=5422439311196834318>💡</emoji> | <b>Доступно:</b> {available_langs}
        """
    },
    "ua": {
        "success": "<emoji id=5447309366568953338>🇺🇦</emoji> Мову встановлено: {lang}",
        "error": "❌ Помилка встановлення мови",
        "invalid": "❌ Невірна мова! Доступно: {langs}",
        "usage": "🌐 Доступні мови: {langs}\n💡 Використання: <code>{my_prefix}setlang en</code>",
        "set_lang" : """
<emoji id=5447410659077661506>🌐</emoji> | <b>Текущий язык:</b> {current_lang}
<emoji id=5395444784611480792>🔧</emoji> | <b>Глобальный язык:</b> {global_lang}
<emoji id=5422439311196834318>💡</emoji> | <b>Доступно:</b> {available_langs}
        """
    }
}

def get_lang_config():
    lang_config_path = Path("userdata/language.ini")
    
    if lang_config_path.exists():
        config = configparser.ConfigParser()
        config.read(lang_config_path)
        return config.get("language", "lang", fallback="en") 
    else:
        return "en"

def save_lang_config(lang: str):
    lang_config_path = Path("userdata/language.ini")
    
    lang_config_path.parent.mkdir(exist_ok=True)
    
    config = configparser.ConfigParser()
    
    if lang_config_path.exists():
        config.read(lang_config_path)
    
    if not config.has_section("language"):
        config.add_section("language")
    config.set("language", "lang", lang) 
    
    with open(lang_config_path, "w") as f:
        config.write(f)


@Client.on_message(fox_command("setlang", Module_Name, filename, "[lang]") & fox_sudo())
async def set_language(client, message):
    message = await who_message(client, message)
    
    if len(message.text.split()) < 2:
        available_langs = ", ".join(all_lang) 
        usage_text = LANGUAGES[get_lang_config()]["usage"].format(
            langs=available_langs, 
            my_prefix=my_prefix()
        )
        await message.edit(usage_text)
        return
    
    lang = message.text.split()[1].lower()
    current_lang = get_lang_config()
    
    if lang in all_lang: 
        save_lang_config(lang)
        
        if set_global_lang(lang):
            success_text = LANGUAGES.get(lang, LANGUAGES["en"])["success"].format(lang=lang.upper())
            await message.edit(success_text)
        else:
            error_text = LANGUAGES.get(current_lang, LANGUAGES["en"])["error"]
            await message.edit(error_text)
    else:
        available_langs = ", ".join(all_lang)
        invalid_text = LANGUAGES.get(current_lang, LANGUAGES["en"])["invalid"].format(langs=available_langs)
        await message.edit(invalid_text)


@Client.on_message(fox_command("getlang", Module_Name, filename) & fox_sudo())
async def get_current_language(client, message):
    message = await who_message(client, message)
    
    current_lang = get_lang_config()
    global_lang = get_global_lang()
    available_langs = ", ".join(all_lang)
    text = LANGUAGES.get(current_lang, LANGUAGES["en"])["set_lang"].format(
        current_lang=current_lang.upper(),
        global_lang=global_lang,
        available_langs=available_langs
    )
    
    await message.edit(text)
