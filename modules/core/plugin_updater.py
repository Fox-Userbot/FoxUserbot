# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import sys
import importlib
from importlib.machinery import SourceFileLoader
from pathlib import Path

from pyrogram import Client

from command import fox_command, fox_sudo, who_message, get_text, get_update_registry

filename = os.path.basename(__file__)
Module_Name = 'Updater'

LANGUAGES = {
    "en": {
        "checking": "<emoji id='5190903199137013741'>🔍</emoji> <b>Checking for plugin updates...</b>",
        "no_updates": "<emoji id='5237699328843200968'>✅</emoji> <b>All plugins up to date</b>",
        "updates_found": "<emoji id='5199688114126400453'>🔄</emoji> <b>Updates available for:</b>\n{list}\n\n<code>{prefix}updatemod &lt;name/all&gt;</code> to update",
        "updated": "<emoji id='5237699328843200968'>✅</emoji> <b>Module {name} updated successfully!</b>",
        "update_failed": "<emoji id='5210952531676504517'>❌</emoji> <b>Failed to update {name}</b>\n<code>{error}</code>",
        "no_module": "<emoji id='5210952531676504517'>❌</emoji> <b>Module {name} not found or has no UPDATE_URL</b>",
        "no_url": "<emoji id='5210952531676504517'>❌</emoji> <b>No UPDATE_URL found in {name}</b>",
        "auto_on": "<emoji id='5237699328843200968'>✅</emoji> <b>Auto-update enabled{target}</b>",
        "auto_off": "<emoji id='5210952531676504517'>❌</emoji> <b>Auto-update disabled{target}</b>",
        "auto_status": "⚙️ <b>Auto-update:</b> global=<code>{global_state}</code>\n{per_module}",
        "startup_updates": "<emoji id='5199688114126400453'>🔄</emoji> <b>Updates available:</b>\n{list}",
        "startup_auto_updated": "<emoji id='5237699328843200968'>✅</emoji> <b>Auto-updated:</b> {list}",
    },
    "ru": {
        "checking": "<emoji id='5190903199137013741'>🔍</emoji> <b>Проверка обновлений плагинов...</b>",
        "no_updates": "<emoji id='5237699328843200968'>✅</emoji> <b>Все плагины обновлены</b>",
        "updates_found": "<emoji id='5199688114126400453'>🔄</emoji> <b>Доступны обновления для:</b>\n{list}\n\n<code>{prefix}updatemod &lt;name/all&gt;</code> для обновления",
        "updated": "<emoji id='5237699328843200968'>✅</emoji> <b>Модуль {name} успешно обновлён!</b>",
        "update_failed": "<emoji id='5210952531676504517'>❌</emoji> <b>Не удалось обновить {name}</b>\n<code>{error}</code>",
        "no_module": "<emoji id='5210952531676504517'>❌</emoji> <b>Модуль {name} не найден или нет UPDATE_URL</b>",
        "no_url": "<emoji id='5210952531676504517'>❌</emoji> <b>Нет UPDATE_URL в {name}</b>",
        "auto_on": "<emoji id='5237699328843200968'>✅</emoji> <b>Автообновление включено{target}</b>",
        "auto_off": "<emoji id='5210952531676504517'>❌</emoji> <b>Автообновление выключено{target}</b>",
        "auto_status": "⚙️ <b>Автообновление:</b> global=<code>{global_state}</code>\n{per_module}",
        "startup_updates": "<emoji id='5199688114126400453'>🔄</emoji> <b>Доступны обновления:</b>\n{list}",
        "startup_auto_updated": "<emoji id='5237699328843200968'>✅</emoji> <b>Автообновлено:</b> {list}",
    },
    "ua": {
        "checking": "<emoji id='5190903199137013741'>🔍</emoji> <b>Перевірка оновлень плагінів...</b>",
        "no_updates": "<emoji id='5237699328843200968'>✅</emoji> <b>Всі плагіни оновлені</b>",
        "updates_found": "<emoji id='5199688114126400453'>🔄</emoji> <b>Доступні оновлення для:</b>\n{list}\n\n<code>{prefix}updatemod &lt;name/all&gt;</code> для оновлення",
        "updated": "<emoji id='5237699328843200968'>✅</emoji> <b>Модуль {name} успішно оновлено!</b>",
        "update_failed": "<emoji id='5210952531676504517'>❌</emoji> <b>Не вдалося оновити {name}</b>\n<code>{error}</code>",
        "no_module": "<emoji id='5210952531676504517'>❌</emoji> <b>Модуль {name} не знайдено або нема UPDATE_URL</b>",
        "no_url": "<emoji id='5210952531676504517'>❌</emoji> <b>Нема UPDATE_URL в {name}</b>",
        "auto_on": "<emoji id='5237699328843200968'>✅</emoji> <b>Автооновлення увімкнено{target}</b>",
        "auto_off": "<emoji id='5210952531676504517'>❌</emoji> <b>Автооновлення вимкнено{target}</b>",
        "auto_status": "⚙️ <b>Автооновлення:</b> global=<code>{global_state}</code>\n{per_module}",
        "startup_updates": "<emoji id='5199688114126400453'>🔄</emoji> <b>Доступні оновлення:</b>\n{list}",
        "startup_auto_updated": "<emoji id='5237699328843200968'>✅</emoji> <b>Автооновлено:</b> {list}",
    }
}

# Dev inserts 1 line:
# UPDATE_URL = "https://raw.githubusercontent.com/FoxUserbot/CustomModules/main/ai.py"
# or checkupdate("https://...", filename)  (compatible with example_edit.py:14)
UPDATE_RE = re.compile(r'UPDATE_URL\s*=\s*["\']([^"\']+)["\']')
CHECKUPDATE_RE = re.compile(r'checkupdate\s*\(\s*["\']([^"\']+)["\']')

CONFIG_PATH = Path("userdata/autoupdate.json")
CACHE_PATH = Path("temp/plugin_update_cache.json")


def _load_config():
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {"global": bool(data.get("global", False)), "modules": dict(data.get("modules", {}))}
    except Exception:
        pass
    return {"global": False, "modules": {}}


def _save_config(cfg):
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def is_auto_enabled(module_stem: str) -> bool:
    cfg = _load_config()
    # per-module overrides global
    if module_stem in cfg["modules"]:
        return bool(cfg["modules"][module_stem])
    return bool(cfg["global"])


def _strip_update_lines(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = str(data)
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # ignore metadata lines for hash comparison (so adding UPDATE_URL doesn't trigger diff)
        if UPDATE_RE.search(line) or CHECKUPDATE_RE.search(line):
            continue
        out.append(line)
    return "\n".join(out).encode("utf-8")


def normalize_bytes(data: bytes) -> bytes:
    """Fix CRLF/LF + trailing spaces issue user met when hashing."""
    # first strip update meta lines, then normalize
    data = _strip_update_lines(data)
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = data.decode("utf-8", errors="ignore") if isinstance(data, bytes) else str(data)
    # normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # strip trailing spaces per line, remove trailing empty lines
    lines = [l.rstrip() for l in text.split("\n")]
    # remove trailing empty lines at EOF (common difference)
    while lines and lines[-1] == "":
        lines.pop()
    # also strip leading empty? keep as is
    return "\n".join(lines).encode("utf-8")


def normalized_hash(data: bytes) -> str:
    return hashlib.sha256(normalize_bytes(data)).hexdigest()


def extract_update_url(file_path: str) -> str | None:
    # 1) try registry from checkupdate() calls executed at import time (only if actually executed, not commented)
    fname = os.path.basename(file_path)
    reg = get_update_registry()
    if fname in reg:
        # verify file actually contains uncommented checkupdate to avoid false positive from example comment
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as rf:
                for line in rf:
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if "checkupdate" in line and reg[fname] in line:
                        return reg[fname]
        except Exception:
            pass
    # 2) parse file content line by line, ignore commented lines
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                m = UPDATE_RE.search(line)
                if m:
                    return m.group(1).strip()
                m2 = CHECKUPDATE_RE.search(line)
                if m2:
                    return m2.group(1).strip()
    except Exception:
        pass
    return None


def fetch_remote(url: str, timeout: int = 7) -> bytes | None:
    # try urllib first (no extra deps), fallback to requests/wget if available
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "FoxUserbot-Updater/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        # fallback to requests if installed
        try:
            import requests
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "FoxUserbot-Updater/1.0"})
            r.raise_for_status()
            return r.content
        except Exception:
            pass
    return None


def _iter_plugin_handlers(module):
    for obj in module.__dict__.values():
        if callable(obj) and hasattr(obj, "handlers"):
            for h in getattr(obj, "handlers", []):
                yield h


def _remove_module_handlers(client: Client, module_qualname: str):
    try:
        mod = importlib.import_module(module_qualname)
    except Exception:
        module_stem = module_qualname.rsplit('.', 1)[-1]
        module_path = os.path.join('modules', 'loaded', f'{module_stem}.py')
        if os.path.exists(module_path):
            try:
                mod = SourceFileLoader(module_qualname, module_path).load_module()
            except Exception:
                return
        else:
            return
    for h in list(_iter_plugin_handlers(mod)):
        try:
            handler, group = h
            if hasattr(client.dispatcher, 'groups') and group in client.dispatcher.groups:
                if handler in client.dispatcher.groups[group]:
                    client.remove_handler(handler, group)
        except Exception:
            pass
    sys.modules.pop(module_qualname, None)


def _load_module_handlers(client: Client, module_qualname: str):
    importlib.invalidate_caches()
    if module_qualname in sys.modules:
        mod = importlib.reload(sys.modules[module_qualname])
    else:
        try:
            mod = importlib.import_module(module_qualname)
        except Exception:
            module_stem = module_qualname.rsplit('.', 1)[-1]
            module_path = os.path.join('modules', 'loaded', f'{module_stem}.py')
            mod = SourceFileLoader(module_qualname, module_path).load_module()
    for h in _iter_plugin_handlers(mod):
        client.add_handler(*h)


def check_single_module(file_path: str) -> dict:
    """Return {has_update:bool, url, error}"""
    url = extract_update_url(file_path)
    if not url:
        return {"has_update": False, "url": None, "error": "no_url"}
    try:
        with open(file_path, "rb") as f:
            local = f.read()
    except Exception as e:
        return {"has_update": False, "url": url, "error": str(e)}
    remote = fetch_remote(url)
    if remote is None:
        return {"has_update": False, "url": url, "error": "fetch_failed"}
    lh = normalized_hash(local)
    rh = normalized_hash(remote)
    return {"has_update": lh != rh, "url": url, "error": None, "local_hash": lh, "remote_hash": rh, "remote_content": remote}


def apply_update(client: Client, module_stem: str, url: str = None, remote_content: bytes = None) -> tuple[bool, str]:
    from modules.core.plugin_validator import PluginValidator
    loaded_path = os.path.join("modules", "loaded", f"{module_stem}.py")
    if not os.path.exists(loaded_path):
        return False, "file not found"
    if url is None:
        url = extract_update_url(loaded_path)
        if not url:
            return False, "no UPDATE_URL"
    if remote_content is None:
        remote_content = fetch_remote(url)
        if remote_content is None:
            return False, "fetch failed"
    # write to temp and validate
    tmp = os.path.join("temp", f"_update_{module_stem}.py")
    try:
        os.makedirs("temp", exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(remote_content)
        validator = PluginValidator()
        success, final_path, msg = validator.validate_and_convert_plugin(tmp, f"{module_stem}.py")
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        if not success:
            return False, msg
        # reload handlers
        qual = f"modules.loaded.{module_stem}"
        try:
            _remove_module_handlers(client, qual)
        except Exception:
            pass
        _load_module_handlers(client, qual)
        return True, "ok"
    except Exception as e:
        return False, str(e)


def scan_all() -> dict:
    """Scan modules/loaded, return {stem: {has_update, url, error}}"""
    result = {}
    loaded_dir = "modules/loaded"
    if not os.path.exists(loaded_dir):
        return result
    for fname in os.listdir(loaded_dir):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        stem = os.path.splitext(fname)[0]
        fpath = os.path.join(loaded_dir, fname)
        info = check_single_module(fpath)
        # only include modules that have UPDATE_URL
        if info["url"] is not None:
            result[stem] = info
    return result


async def check_updates_on_start(client: Client):
    """Called from main.py @client.on_start — notifies in restart chat or silently."""
    try:
        scan = scan_all()
        if not scan:
            return
        updates = {k: v for k, v in scan.items() if v.get("has_update")}
        if not updates:
            return
        # determine notify target: sys.argv[1] from restarter (chat_id)
        chat_id = None
        thread_id = None
        if len(sys.argv) >= 2:
            try:
                raw = sys.argv[1]
                if raw and raw != "None":
                    try:
                        chat_id = int(raw)
                    except:
                        chat_id = raw
            except Exception:
                pass
        if len(sys.argv) >= 5 and sys.argv[4] != "None":
            try:
                thread_id = int(sys.argv[4])
            except:
                thread_id = None
        # auto-update enabled modules
        auto_done = []
        still_need = []
        for stem, info in updates.items():
            if is_auto_enabled(stem):
                ok, _ = apply_update(client, stem, info["url"], info.get("remote_content"))
                if ok:
                    auto_done.append(stem)
                else:
                    still_need.append(stem)
            else:
                still_need.append(stem)
        from command import my_prefix
        prefix = my_prefix()
        if auto_done:
            txt = get_text("plugin_updater", "startup_auto_updated", LANGUAGES=LANGUAGES, list=", ".join(f"<code>{s}</code>" for s in auto_done))
            try:
                if chat_id:
                    await client.send_message(chat_id, txt, message_thread_id=thread_id)
                else:
                    await client.send_message("me", txt)
            except Exception:
                pass
        if still_need:
            lst = "\n".join(f"• <code>{s}</code>" for s in still_need)
            txt = get_text("plugin_updater", "startup_updates", LANGUAGES=LANGUAGES, list=lst)
            try:
                if chat_id:
                    await client.send_message(chat_id, txt, message_thread_id=thread_id)
                else:
                    # don't spam if no restart context — just log
                    import logging
                    logging.info(f"[Updater] Updates available: {', '.join(still_need)}")
                    # also send to me as fallback (can be disabled if too noisy)
                    await client.send_message("me", txt)
            except Exception:
                pass
    except Exception as e:
        import logging
        logging.warning(f"[Updater] startup check failed: {e}")


# === Commands ===

@Client.on_message(fox_command("checkupdates", Module_Name, filename) & fox_sudo())
async def checkupdates_cmd(client, message):
    message = await who_message(client, message)
    await message.edit(get_text("plugin_updater", "checking", LANGUAGES=LANGUAGES))
    scan = scan_all()
    if not scan:
        await message.edit(get_text("plugin_updater", "no_updates", LANGUAGES=LANGUAGES))
        return
    updates = {k: v for k, v in scan.items() if v.get("has_update")}
    if not updates:
        await message.edit(get_text("plugin_updater", "no_updates", LANGUAGES=LANGUAGES))
        return
    from command import my_prefix
    prefix = my_prefix()
    lst = "\n".join(f"• <code>{k}</code>" for k in updates)
    txt = get_text("plugin_updater", "updates_found", LANGUAGES=LANGUAGES, list=lst, prefix=prefix)
    await message.edit(txt)


@Client.on_message(fox_command(["updatemod", "update_mod"], Module_Name, filename, "[name/all]") & fox_sudo())
async def updatemod_cmd(client, message):
    message = await who_message(client, message)
    args = (message.text or "").split()
    if len(args) < 2:
        await message.edit(get_text("plugin_updater", "checking", LANGUAGES=LANGUAGES))
        scan = scan_all()
        updates = {k: v for k, v in scan.items() if v.get("has_update")}
        if not updates:
            await message.edit(get_text("plugin_updater", "no_updates", LANGUAGES=LANGUAGES))
            return
        from command import my_prefix
        prefix = my_prefix()
        lst = "\n".join(f"• <code>{k}</code>" for k in updates)
        txt = get_text("plugin_updater", "updates_found", LANGUAGES=LANGUAGES, list=lst, prefix=prefix)
        await message.edit(txt)
        return
    target = args[1].strip()
    if target.lower() == "all":
        scan = scan_all()
        updates = {k: v for k, v in scan.items() if v.get("has_update")}
        if not updates:
            await message.edit(get_text("plugin_updater", "no_updates", LANGUAGES=LANGUAGES))
            return
        done = []
        failed = []
        for stem in list(updates.keys()):
            ok, err = apply_update(client, stem, updates[stem]["url"], updates[stem].get("remote_content"))
            if ok:
                done.append(stem)
            else:
                failed.append(f"{stem}: {err}")
        if done:
            await message.edit(get_text("plugin_updater", "updated", LANGUAGES=LANGUAGES, name=", ".join(done)))
        if failed:
            await message.edit(get_text("plugin_updater", "update_failed", LANGUAGES=LANGUAGES, name="all", error="; ".join(failed)))
        return
    # single module
    stem = target[:-3] if target.endswith(".py") else target
    fpath = os.path.join("modules", "loaded", f"{stem}.py")
    if not os.path.exists(fpath):
        await message.edit(get_text("plugin_updater", "no_module", LANGUAGES=LANGUAGES, name=stem))
        return
    url = extract_update_url(fpath)
    if not url:
        await message.edit(get_text("plugin_updater", "no_url", LANGUAGES=LANGUAGES, name=stem))
        return
    info = check_single_module(fpath)
    if info.get("error") and info["error"] != "no_url":
        pass  # still try to update
    ok, err = apply_update(client, stem, url, info.get("remote_content"))
    if ok:
        await message.edit(get_text("plugin_updater", "updated", LANGUAGES=LANGUAGES, name=stem))
    else:
        await message.edit(get_text("plugin_updater", "update_failed", LANGUAGES=LANGUAGES, name=stem, error=err))


@Client.on_message(fox_command("autoupdate", Module_Name, filename, "[on/off] [module]") & fox_sudo())
async def autoupdate_cmd(client, message):
    message = await who_message(client, message)
    args = (message.text or "").split()
    # !autoupdate -> show status
    if len(args) == 1:
        cfg = _load_config()
        per = "\n".join(f"• <code>{k}</code> = {v}" for k, v in cfg["modules"].items()) or "(no per-module)"
        txt = get_text("plugin_updater", "auto_status", LANGUAGES=LANGUAGES, global_state=str(cfg["global"]), per_module=per)
        await message.edit(txt)
        return
    # !autoupdate on/off [module]
    state_raw = args[1].lower()
    if state_raw not in ("on", "off", "enable", "disable", "1", "0", "true", "false"):
        # maybe !autoupdate <module> on ?
        if len(args) >= 3:
            state_raw = args[2].lower()
            module_raw = args[1]
        else:
            return await message.edit("Usage: <code>autoupdate on/off [module]</code>")
    else:
        module_raw = args[2] if len(args) >= 3 else None
    enable = state_raw in ("on", "enable", "1", "true")
    cfg = _load_config()
    if module_raw:
        stem = module_raw[:-3] if module_raw.endswith(".py") else module_raw
        cfg["modules"][stem] = enable
        _save_config(cfg)
        key = "auto_on" if enable else "auto_off"
        await message.edit(get_text("plugin_updater", key, LANGUAGES=LANGUAGES, target=f" for <code>{stem}</code>"))
    else:
        cfg["global"] = enable
        _save_config(cfg)
        key = "auto_on" if enable else "auto_off"
        await message.edit(get_text("plugin_updater", key, LANGUAGES=LANGUAGES, target=" (global)"))
