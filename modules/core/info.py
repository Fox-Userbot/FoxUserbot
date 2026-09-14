# -*- coding: utf-8 -*-
import configparser
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from platform import python_version, release, system, uname

from command import fox_command, fox_sudo, who_message, get_text
from modules.core.uptime import bot_start_time
from pyrogram import Client, __version__

DEFAULT_INFO_IMAGE = "https://raw.githubusercontent.com/Fox-Userbot/FoxUserbot/refs/heads/main/photos/FoxUB_info.jpg"
THEME_PATH = "userdata/theme.ini"

LANGUAGES = {
    "en": {
        "default_text": """
<emoji id="5190875290439525089">🦊</emoji><b> | FoxUserbot INFO</b>
<emoji id="5372878077250519677">🐍</emoji><b> | Python: {python_version}</b>
<emoji id="5190637731503415052">🥧</emoji><b> | Kurigram: {pyrogram_version}</b>
<emoji id="5282843764451195532">⏰</emoji><b> | Uptime: {uptime}</b>
<emoji id="5350554349074391003">💻</emoji><b> | Platform: {hosting} | {platform}</b>
<emoji id="5420323339723881652">🛡️</emoji><b> | Safe Mode: {safe_mode}</b>
    
<emoji id="5330237710655306682">💻</emoji><a href="https://t.me/foxteam0"><b> | Official FoxTeam Channel.</b></a>
<emoji id="5346181118884331907">🐈‍⬛</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot"><b> | Github Repository.</b></a>
<emoji id="5379999674193172777">🤔</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot#how-to-install"><b> | Installation Guide.</b></a>
    
<emoji id=5350554349074391003>💻</emoji> | <b>Developers:</b>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/a9_fm">A9FM</a>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/ArThirtyFour">ArThirtyFour</a>

<emoji id="5359480394922082925">🖼</emoji> | <b>Designer:</b>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/nw_off">Nw_Off</a>
"""
    },
    "ru": {
        "default_text": """
<emoji id="5190875290439525089">🦊</emoji><b> | FoxUserbot ИНФО</b>
<emoji id="5372878077250519677">🐍</emoji><b> | Python: {python_version}</b>
<emoji id="5190637731503415052">🥧</emoji><b> | Kurigram: {pyrogram_version}</b>
<emoji id="5282843764451195532">⏰</emoji><b> | Время работы: {uptime}</b>
<emoji id="5350554349074391003">💻</emoji><b> | Платформа: {hosting} | {platform}</b>
<emoji id="5420323339723881652">🛡️</emoji><b> | Безопасный режим: {safe_mode}</b>
    
<emoji id="5330237710655306682">💻</emoji><a href="https://t.me/foxteam0"><b> | Официальный канал FoxTeam.</b></a>
<emoji id="5346181118884331907">🐈‍⬛</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot"><b> | Github репозиторий.</b></a>
<emoji id="5379999674193172777">🤔</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot#how-to-install"><b> | Руководство по установке.</b></a>
    
<emoji id=5350554349074391003>💻</emoji> | <b>Разработчики:</b>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/a9_fm">A9FM</a>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/ArThirtyFour">ArThirtyFour</a>

<emoji id="5359480394922082925">🖼</emoji> | <b>Дизайнер:</b>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/nw_off">Nw_Off</a>
"""
    },
    "ua": {
        "default_text": """
<emoji id="5190875290439525089">🦊</emoji><b> | FoxUserbot ІНФО</b>
<emoji id="5372878077250519677">🐍</emoji><b> | Python: {python_version}</b>
<emoji id="5190637731503415052">🥧</emoji><b> | Kurigram: {pyrogram_version}</b>
<emoji id="5282843764451195532">⏰</emoji><b> | Час роботи: {uptime}</b>
<emoji id="5350554349074391003">💻</emoji><b> | Платформа: {hosting} | {platform}</b>
<emoji id="5420323339723881652">🛡️</emoji><b> | Безпечний режим: {safe_mode}</b>
    
<emoji id="5330237710655306682">💻</emoji><a href="https://t.me/foxteam0"><b> | Офіційний канал FoxTeam.</b></a>
<emoji id="5346181118884331907">🐈‍⬛</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot"><b> | Github репозиторій.</b></a>
<emoji id="5379999674193172777">🤔</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot#how-to-install"><b> | Посібник з встановлення.</b></a>
    
<emoji id=5350554349074391003>💻</emoji> | <b>Розробники:</b>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/a9_fm">A9FM</a>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/ArThirtyFour">ArThirtyFour</a>

<emoji id="5359480394922082925">🖼</emoji> | <b>Дизайнер:</b>
<emoji id="5330237710655306682">📞</emoji> | <a href="https://t.me/nw_off">Nw_Off</a>
"""
    }
}

def linux_distro():
    # /etc/os-release 
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release", "r", encoding='utf-8') as f:
            lines = f.readlines()
        os_info = {}
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                os_info[key] = value.strip('"')
        
        name = os_info.get("NAME", "Unknown")
        version = os_info.get("VERSION_ID", "Unknown")

        if name == "Arch Linux":
            return ("Arch", version)
        elif name == "Kali GNU/Linux":
            return ("Kali Linux", version)
        elif "Fedora" in name:
            return ("Fedora", version)
        elif "CentOS" in name:
            return ("CentOS", version)
        elif "openSUSE" in name:
            return ("openSUSE", version)
        elif "Alpine" in name:
            return ("Alpine", version)
        return (name, version)

    # /etc/lsb-release
    elif os.path.exists("/etc/lsb-release"):
        with open("/etc/lsb-release", "r", encoding='utf-8') as f:
            lines = f.readlines()
        distro_info = {}
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                distro_info[key] = value.strip('"')

        if "DISTRIB_ID" in distro_info:
            name = distro_info["DISTRIB_ID"]
            version = distro_info.get("DISTRIB_RELEASE", "Unknown")
            return (name, version)

    # /etc/redhat-release (RHEL, CentOS, Fedora)
    elif os.path.exists("/etc/redhat-release"):
        with open("/etc/redhat-release", "r", encoding='utf-8') as f:
            content = f.read().strip()
        
        if "release" in content:
            parts = content.split("release")
            name = parts[0].strip()
            version = parts[1].strip().split()[0] if len(parts) > 1 else "Unknown"
            
            if "CentOS" in name:
                name = "CentOS"
            elif "Fedora" in name:
                name = "Fedora"
            elif "Red Hat" in name:
                name = "RHEL"
            
            return (name, version)
        else:
            return (content, "Unknown")
    
    # /etc/debian_version
    elif os.path.exists("/etc/debian_version"):
        with open("/etc/debian_version", "r", encoding='utf-8') as f:
            version = f.read().strip()
        return ("Debian", version)
    
    # Alpine Linux
    elif os.path.exists("/etc/alpine-release"):
        with open("/etc/alpine-release", "r", encoding='utf-8') as f:
            version = f.read().strip()
        return ("Alpine", version)
    
    # Gentoo
    elif os.path.exists("/etc/gentoo-release"):
        with open("/etc/gentoo-release", "r", encoding='utf-8') as f:
            content = f.read().strip()
        return ("Gentoo", content.split()[-1] if content.split() else "Unknown")
    
    else:
        return ("Unknown", "Unknown")
    
def raspberry_pi():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        if 'BCM' in cpuinfo:
            model_match = re.search(r'Model\s*:\s*(.+)', cpuinfo)
            hardware_match = re.search(r'Hardware\s*:\s*(.+)', cpuinfo)
            if model_match:
                model_name = model_match.group(1).strip()
                return model_name
            elif hardware_match:
                hardware_name = hardware_match.group(1).strip()
                return hardware_name
            else:
                return "Raspberry Pi"
    except:
        return None

def hosting_text():
    os_release = release()
    raspberry_pi_version = raspberry_pi()
    termux_vars = [
        'TERMUX_VERSION',
        'TERMUX_APK_RELEASE',
        'PREFIX',
    ]
    if any(var in os.environ for var in termux_vars):
        return '<emoji id="5301286542998774155">📱</emoji> Termux'
    elif "microsoft-standard" in uname().release:
        return '<emoji id="6298333093044422573">😥</emoji> WSL'
    elif "TEAHOST" in os.environ:
        return f'<emoji id="5463032631954250729">☕️</emoji> TeaHost'
    elif "azure" in os_release.lower():
        return '<emoji id="5301233040591169044">👩‍💻</emoji> Azure'
    elif raspberry_pi_version != None:
        return f'<emoji id="5274111069441238993">🍇</emoji> {raspberry_pi_version}'
    elif "DOCKER" in os.environ:
        return '<emoji id="5301137237050663843">👩‍💻</emoji> Docker'
    else:
        return '<emoji id="5807465992363710697">💎</emoji> VPS'

def get_platform_info() -> str:
    os_name = system()
    os_release = release()
    distributive, distro_version = linux_distro()
    if distributive == "Kali Linux":
        return f'<emoji id="5300820182564872893">🐧</emoji> Kali Linux {distro_version}'
    if distributive == "Ubuntu":
        return f'<emoji id="5300985968302498775">🐧</emoji> Ubuntu {distro_version}'
    if distributive == "Debian":
        return f'<emoji id="5300838891442413975">🐧</emoji> Debian {distro_version}'
    if distributive == "CachyOS Linux":
        return f'<emoji id="5301033874367717956">🐧</emoji> CachyOS {distro_version}'
    if distributive == "Arch":
        return f'<emoji id="5301033874367717956">🐧</emoji> Arch Linux {distro_version}'
    if distributive == "Fedora":
        return f'<emoji id="5276366700365751434">🐧</emoji> Fedora {distro_version}'
    if distributive == "Alpine":
        return f'<emoji id="5386746268951258721">🐧</emoji> Alpine {distro_version}'
    if distributive == "Unknown":
        os_names = {
            'Linux': '<emoji id="5300957668762987048">🐧</emoji> Linux',
            'Windows': '<emoji id="5366318141771096216">👩‍💻</emoji> Windows', 
            'Darwin': '<emoji id="5301155675345265040">🍏</emoji> macOS',
        }
        try:
            os_display = os_names.get(os_name, f'💻 {os_name}')
            return f"{os_display} ({os_release})"
        except:
            return f"💻 {os_name} ({os_release})"
    else:
        return f'<emoji id="5300957668762987048">🐧</emoji> {distributive} ({distro_version})'

def format_uptime():
    uptime = datetime.now() - bot_start_time()
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    result = []
    if days > 0:
        result.append(f"{days} days")
    if hours > 0:
        result.append(f"{hours} hours")
    if minutes > 0:
        result.append(f"{minutes} minutes")
    if not result:
        result.append(f"{seconds} seconds")
    
    return ' '.join(result)

def get_safe_mode_status():
    return "--safe" in sys.argv

def replace_aliases(text, message):
    uptime_text = format_uptime()
    platform_text = get_platform_info()
    safe_mode = get_safe_mode_status()
    hosting = hosting_text()
    
    aliases = {
        '{version}': __version__,
        '{python_version}': python_version(),
        '{uptime}': uptime_text,
        '{hosting}': hosting,
        '{platform}': platform_text,
        '{safe_mode}': 'Enabled' if safe_mode else 'Disabled',
    }

    for alias, value in aliases.items():
        text = text.replace(alias, str(value))

    footer = f"""
<blockquote expandable><emoji id="5330237710655306682">💻</emoji><a href="https://t.me/foxteam0"><b> | Official FoxTeam Channel.</b></a>
<emoji id="5346181118884331907">🐈‍⬛</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot"><b> | Github Repository.</b></a>
<emoji id="5379999674193172777">🤔</emoji><a href="https://github.com/Fox-Userbot/FoxUserbot#how-to-install"><b> | Installation Guide.</b></a></blockquote>
"""
    return text + footer

def get_info_image():
    if not Path(THEME_PATH).exists():
        return DEFAULT_INFO_IMAGE

    try:
        config = configparser.ConfigParser()
        config.read(THEME_PATH, encoding='utf-8')
        return config.get("info", "image", fallback=DEFAULT_INFO_IMAGE)
    except:
        return DEFAULT_INFO_IMAGE

def get_info_text(message):
    uptime_text = format_uptime()
    platform_text = get_platform_info()
    safe_mode = get_safe_mode_status()
    hosting = hosting_text()
    
    custom_text = None
    if Path(THEME_PATH).exists():
        try:
            config = configparser.ConfigParser()
            config.read(THEME_PATH, encoding='utf-8')
            custom_text = config.get("info", "text", fallback=None)
            if custom_text and custom_text.strip() and custom_text != "Not set":
                return replace_aliases(custom_text, message)
        except Exception as e:
            pass
    
    default_text = get_text("info", "default_text", LANGUAGES=LANGUAGES)
    return default_text.format(
        python_version=python_version(),
        pyrogram_version=__version__,
        uptime=uptime_text,
        hosting=hosting,
        platform=platform_text,
        safe_mode='Enabled' if safe_mode else 'Disabled'
    )

@Client.on_message(fox_command("info", "info", os.path.basename(__file__)) & fox_sudo())
async def info(client, message):
    message = await who_message(client, message)
    try:
        media_url = get_info_image()
        info_text = get_info_text(message)
        file_extension = media_url.split(".")[-1]
        if file_extension in ["mp4", "mov", "avi", "mkv", "webm"]:
            await client.send_video(
                message.chat.id, 
                video=media_url, 
                caption=info_text,
                message_thread_id=message.message_thread_id
            )
        elif file_extension == "gif":
            await client.send_animation(
                message.chat.id, 
                animation=media_url, 
                caption=info_text,
                message_thread_id=message.message_thread_id
            )
        else:           
            await client.send_photo(
                message.chat.id, 
                photo=media_url, 
                caption=info_text,
                message_thread_id=message.message_thread_id
            )
        await message.delete()
    except Exception as e:
        print(f"Error: {e}")
        try:
            await client.send_photo(
                message.chat.id, 
                photo=DEFAULT_INFO_IMAGE, 
                caption=get_info_text(message), 
                message_thread_id=message.message_thread_id
            )
            await message.delete()
        except:
            try:
                await client.send_photo(
                    message.chat.id, 
                    photo="photos/FoxUB_info.jpg", 
                    caption=get_info_text(message), 
                    message_thread_id=message.message_thread_id
                )
                await message.delete()
            except:
                await message.edit(get_info_text(message))