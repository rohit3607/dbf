# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import time
from asyncio import sleep
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges, ReplyKeyboardRemove
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from plugins.start import *
from config import *
from helper_func import *
from database.database import *


BAN_SUPPORT = f"{BAN_SUPPORT}"

#=====================================================================================##

@Bot.on_message(filters.command('stats') & admin)
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))


#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & admin)
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await db.full_userbase()
    await msg.edit(f"{len(users)} ᴜsᴇʀs ᴀʀᴇ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ")

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

#=====================================================================================##

#AUTO-DELETE

@Bot.on_message(filters.private & filters.command('dlt_time') & admin)
async def set_delete_time(client: Bot, message: Message):
    try:
        duration = int(message.command[1])

        await db.set_del_timer(duration)

        await message.reply(f"<b>Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ <blockquote>{duration} sᴇᴄᴏɴᴅs.</blockquote></b>")

    except (IndexError, ValueError):
        await message.reply("<b>Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs.</b> Usage: /dlt_time {duration}")

@Bot.on_message(filters.private & filters.command('check_dlt_time') & admin)
async def check_delete_time(client: Bot, message: Message):
    duration = await db.get_del_timer()

    await message.reply(f"<b><blockquote>Cᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ɪs sᴇᴛ ᴛᴏ {duration}sᴇᴄᴏɴᴅs.</blockquote></b>")

#=====================================================================================##

# =========================
# /setfile Command (Single-file / media-group support)
# =========================

def _extract_file_ids(msg: Message):
    """Return a list of file_id(s) from supported media in a message."""
    ids = []

    if msg.document:
        ids.append(msg.document.file_id)

    if msg.video:
        ids.append(msg.video.file_id)

    if msg.audio:
        ids.append(msg.audio.file_id)

    if msg.photo:
        ids.append(msg.photo.file_id)

    if msg.voice:
        ids.append(msg.voice.file_id)

    if msg.video_note:
        ids.append(msg.video_note.file_id)

    if msg.animation:
        ids.append(msg.animation.file_id)

    if msg.sticker:
        ids.append(msg.sticker.file_id)

    return ids


@Bot.on_message(filters.command("setfile") & filters.private & admin)
async def set_file_cmd(client: Bot, message: Message):
    """Store a single file or entire media group under a numeric key.

    Usage: /setfile <number>
    Then send one file (or a media group)."""
    if len(message.command) != 2:
        return await message.reply_text(
            "⚠️ Usage:\n`/setfile <number>`\nThen send a single file or media group."
        )

    key = message.command[1].strip()
    if not key.isdigit():
        return await message.reply_text("❌ Only numbers are allowed as keys.")
    # Prevent appending to an existing key
    if await db.key_exists(key):
        return await message.reply_text(
            "⚠️ This key already exists.\nUse /edit to replace the files or /delfile to remove it."
        )

    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)
    await message.reply(
        "📥 Send the file (single file or a media group).\n"
        "If you send a media group (album), all items will be included.\n"
        "Press STOP to cancel.",
        reply_markup=STOP_KEYBOARD
    )

    try:
        user_msg = await client.ask(
            chat_id=message.chat.id,
            text="Waiting for file...",
            timeout=30  # wait 30 seconds for the file
        )
    except asyncio.TimeoutError:
        return await message.reply("❌ Timeout. No file received.", reply_markup=ReplyKeyboardRemove())

    if user_msg.text and user_msg.text.strip().upper() == "STOP":
        return await message.reply("⏹ Operation cancelled.", reply_markup=ReplyKeyboardRemove())

    # Collect messages to extract media and captions
    msgs = []
    if user_msg.media_group_id:
        try:
            msgs = await client.get_media_group(chat_id=message.chat.id, message_id=user_msg.id)
        except Exception:
            msgs = [user_msg]
    else:
        msgs = [user_msg]

    # If this message is part of a media group, try to collect the rest of the group quickly
    if user_msg.media_group_id:
        mgid = user_msg.media_group_id
        while True:
            try:
                more = await client.ask(chat_id=message.chat.id, text="Waiting for rest of media group...", timeout=1)
            except asyncio.TimeoutError:
                break
            if more.text and more.text.strip().upper() == "STOP":
                break
            if getattr(more, "media_group_id", None) == mgid and more.from_user.id == user_msg.from_user.id:
                msgs.append(more)
            else:
                continue

    await message.reply("✅ Collection finished.", reply_markup=ReplyKeyboardRemove())

    if not msgs:
        return await message.reply("❌ No valid media message was received and stored.")

    stored_count = 0
    for m in msgs:
        fids = _extract_file_ids(m)
        if not fids:
            continue
        caption = m.caption.html if m.caption else None
        media_type = (
            "document" if m.document else
            "video" if m.video else
            "photo" if m.photo else
            "audio" if m.audio else
            "voice" if m.voice else
            "animation" if m.animation else
            "sticker" if m.sticker else
            "unknown"
        )
        file_name = m.document.file_name if m.document else None
        for fid in fids:
            await db.add_file_to_key(key, message.chat.id, fid, caption=caption, file_name=file_name, media_type=media_type)
            stored_count += 1

    await message.reply(f"✅ Stored {stored_count} file(s) under key `{key}` successfully.")


# =========================
# /setfiles Command (Channel-based batch collection)
# =========================
@Bot.on_message(filters.command("setfiles") & filters.private & admin)
async def set_files_batch(client: Bot, message: Message):
    """Collect a range of posts from the DB channel and store under a key.

    Usage: /setfiles <number>
    Then forward the FIRST and LAST posts from the DB channel (or send their links).
    """
    if len(message.command) != 2:
        return await message.reply_text("⚠️ Usage:\n`/setfiles <number>`\nThen forward FIRST and LAST DB channel posts.")

    key = message.command[1].strip()
    if not key.isdigit():
        return await message.reply_text("❌ Only numbers are allowed as keys.")
    # Prevent appending to an existing key
    if await db.key_exists(key):
        return await message.reply_text(
            "⚠️ This key already exists.\nUse /edit to replace the files or /delfile to remove it."
        )

    await message.reply(
        f"📥 Forward the FIRST post from <a href='{client.db_channel.invite_link}'>DB Channel</a>.",
        disable_web_page_preview=True
    )
    try:
        first = await client.ask(chat_id=message.chat.id, text="Waiting for FIRST DB channel post...", timeout=60)
    except asyncio.TimeoutError:
        return await message.reply("❌ Timeout. No message received.")
    f_msg_id = await get_message_id(client, first)
    if not f_msg_id:
        return await message.reply("❌ That message isn't from the DB channel.")

    try:
        last = await client.ask(chat_id=message.chat.id, text="Now forward the LAST DB channel post...", timeout=60)
    except asyncio.TimeoutError:
        return await message.reply("❌ Timeout. No message received.")
    s_msg_id = await get_message_id(client, last)
    if not s_msg_id:
        return await message.reply("❌ That message isn't from the DB channel.")

    start = min(f_msg_id, s_msg_id)
    end = max(f_msg_id, s_msg_id)

    MAX_RANGE = 2000
    if end - start + 1 > MAX_RANGE:
        return await message.reply(f"❌ Range too large ({end-start+1}). Please limit to {MAX_RANGE} messages.")

    msg_ids = list(range(start, end + 1))
    msgs = await get_messages(client, msg_ids)

    total_added = 0
    for m in msgs:
        fids = _extract_file_ids(m)
        if not fids:
            continue
        caption = m.caption.html if m.caption else None
        media_type = (
            "document" if m.document else
            "video" if m.video else
            "photo" if m.photo else
            "audio" if m.audio else
            "voice" if m.voice else
            "animation" if m.animation else
            "sticker" if m.sticker else
            "unknown"
        )
        file_name = m.document.file_name if m.document else None
        for fid in fids:
            await db.add_file_to_key(key, client.db_channel.id, fid, caption=caption, file_name=file_name, media_type=media_type)
            total_added += 1

    await message.reply(f"✅ Stored {total_added} files from DB channel under key `{key}` successfully.")
    return

# =========================

# =========================
# /listfile Command
# =========================
@Bot.on_message(filters.command("listfile") & filters.private & admin)
async def list_files_cmd(client: Bot, message: Message):
    files = await db.list_files()
    if not files:
        return await message.reply_text("📂 No files saved yet.")

    text = "📁 <b>Saved Files:</b>\n\n"
    for f in files:
        links = []
        for fid in f["file_ids"]:
            links.append(f"[📎](https://t.me/c/{str(f['chat_id']).replace('-100','')}/{fid})")
        text += f"🔹 <code>{f['key']}</code> → {' '.join(links)}\n"

    await message.reply_text(text, disable_web_page_preview=True)


# =========================
# /delfile Command
# =========================
@Bot.on_message(filters.command("delfile") & filters.private & admin)
async def delete_file_cmd(client: Bot, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("⚠️ Usage:\n`/delfile <number>`")

    key = message.command[1].strip()
    result = await db.delete_file(key)
    if result.deleted_count == 0:
        return await message.reply_text(f"❌ No file found for key `{key}`.")

    await message.reply_text(f"🗑 Deleted all files under key `{key}` successfully.")


# =========================
# /edit Command (Replace files under a key)
# =========================
@Bot.on_message(filters.command("edit") & filters.private & admin)
async def edit_file_cmd(client: Bot, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("⚠️ Usage:\n`/edit <number>`")
    key = message.command[1].strip()
    if not key.isdigit():
        return await message.reply_text("❌ Only numbers are allowed as keys.")
    existing = await db.get_file(key)
    if not existing:
        return await message.reply_text("❌ No existing files for this key. Use /setfile or /setfiles first.")

    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)
    await message.reply(
        "📥 Send new files or forward FIRST and LAST DB channel posts to replace.\n"
        "Press STOP to cancel.",
        reply_markup=STOP_KEYBOARD
    )
    try:
        first = await client.ask(chat_id=message.chat.id, text="Waiting for media or forwarded post...", timeout=60)
    except asyncio.TimeoutError:
        return await message.reply("❌ Timeout. No input received.", reply_markup=ReplyKeyboardRemove())
    if first.text and first.text.strip().upper() == "STOP":
        return await message.reply("⏹ Operation cancelled.", reply_markup=ReplyKeyboardRemove())

    # Try channel-based edit if forwarded
    f_msg_id = await get_message_id(client, first)
    file_ids = []
    file_meta = []
    if f_msg_id:
        try:
            last = await client.ask(chat_id=message.chat.id, text="Forward the LAST DB channel post...", timeout=60)
        except asyncio.TimeoutError:
            return await message.reply("❌ Timeout. No message received.", reply_markup=ReplyKeyboardRemove())
        s_msg_id = await get_message_id(client, last)
        if not s_msg_id:
            return await message.reply("❌ That message isn't from the DB channel.", reply_markup=ReplyKeyboardRemove())
        start = min(f_msg_id, s_msg_id)
        end = max(f_msg_id, s_msg_id)
        MAX_RANGE = 2000
        if end - start + 1 > MAX_RANGE:
            return await message.reply(f"❌ Range too large ({end-start+1}). Please limit to {MAX_RANGE} messages.", reply_markup=ReplyKeyboardRemove())
        msg_ids = list(range(start, end + 1))
        msgs = await get_messages(client, msg_ids)
        for m in msgs:
            fids = _extract_file_ids(m)
            if not fids:
                continue
            caption = m.caption.html if m.caption else None
            media_type = (
                "document" if m.document else
                "video" if m.video else
                "photo" if m.photo else
                "audio" if m.audio else
                "voice" if m.voice else
                "animation" if m.animation else
                "sticker" if m.sticker else
                "unknown"
            )
            file_name = m.document.file_name if m.document else None
            for fid in fids:
                file_ids.append(fid)
                file_meta.append({"file_id": fid, "caption": caption, "file_name": file_name, "media_type": media_type})
        await db.update_key_files(key, client.db_channel.id, file_ids, file_meta)
        await message.reply(f"✅ Replaced files under key `{key}` successfully.", reply_markup=ReplyKeyboardRemove())
        return

    # Otherwise treat as direct media replacement
    msgs = []
    if first.media_group_id:
        try:
            msgs = await client.get_media_group(chat_id=message.chat.id, message_id=first.id)
        except Exception:
            msgs = [first]
    else:
        msgs = [first]
    # Buffer small window to collect additional direct media
    BUFFER_WINDOW = 2.0
    deadline = time.time() + BUFFER_WINDOW
    while True:
        try:
            timeout = deadline - time.time()
            if timeout <= 0:
                break
            nxt = await asyncio.wait_for(client.listen(chat_id=message.chat.id), timeout=timeout)
        except asyncio.TimeoutError:
            break
        if nxt.text and nxt.text.strip().upper() == "STOP":
            break
        if getattr(nxt, "media_group_id", None):
            try:
                grp = await client.get_media_group(chat_id=message.chat.id, message_id=nxt.id)
                msgs.extend(grp)
            except Exception:
                msgs.append(nxt)
        elif (nxt.video or nxt.document or nxt.photo or nxt.audio or nxt.voice or nxt.animation):
            msgs.append(nxt)
    for m in msgs:
        fids = _extract_file_ids(m)
        if not fids:
            continue
        caption = m.caption.html if m.caption else None
        media_type = (
            "document" if m.document else
            "video" if m.video else
            "photo" if m.photo else
            "audio" if m.audio else
            "voice" if m.voice else
            "animation" if m.animation else
            "sticker" if m.sticker else
            "unknown"
        )
        file_name = m.document.file_name if m.document else None
        for fid in fids:
            file_ids.append(fid)
            file_meta.append({"file_id": fid, "caption": caption, "file_name": file_name, "media_type": media_type})
    await db.update_key_files(key, message.chat.id, file_ids, file_meta)
    await message.reply(f"✅ Replaced files under key `{key}` successfully.", reply_markup=ReplyKeyboardRemove())

# =========================
# Auto Send by Key
# =========================
@Bot.on_message(filters.private & filters.text)
async def send_saved_file(client: Bot, message: Message):
    user_id = message.from_user.id

    # ✅ Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # ⛔️ Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # ✅ Check Force Subscription
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # 🕓 File auto-delete time in seconds
    FILE_AUTO_DELETE = await db.get_del_timer()

    text = message.text.strip()
    if text.startswith("/") or not text.isdigit():
        return

    # 🔑 Token verification + Shortlink verification system
    verify_status = await db.get_verify_status(user_id)

    if SHORTLINK_URL or SHORTLINK_API:
        # --- Create new token or refresh if expired ---
        new_token_needed = False
        if not verify_status:
            new_token_needed = True
        else:
            if not verify_status.get("is_verified"):
                new_token_needed = True
            elif VERIFY_EXPIRE < (time.time() - verify_status.get("verified_time", 0)):
                new_token_needed = True

        # --- Generate new verification token ---
        if new_token_needed:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await db.update_verify_status(user_id, verify_token=token, is_verified=False, verified_time=0)
            short_link = await get_shortlink(
                SHORTLINK_URL,
                SHORTLINK_API,
                f'https://telegram.dog/{client.username}?start=verify_{token}'
            )
            btn = [
                [InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ •", url=short_link),
                 InlineKeyboardButton("• ᴛᴜᴛᴏʀɪᴀʟ •", url=TUT_VID)],
                [InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
            ]
            return await message.reply(
                f"⚠️ 𝗬𝗼𝘂𝗿 𝘁𝗼𝗸𝗲𝗻 𝗶𝘀 𝗺𝗶𝘀𝘀𝗶𝗻𝗴 𝗼𝗿 𝗲𝘅𝗽𝗶𝗿𝗲𝗱.\n\n"
                f"<b>Token validity:</b> {get_exp_time(VERIFY_EXPIRE)}\n\n"
                f"Pass one ad to unlock access for {get_exp_time(VERIFY_EXPIRE)}.",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        # --- Handle verification ---
        if "verify_" in message.text:
            try:
                _, token = message.text.split("_", 1)
            except:
                return await message.reply("⚠️ Invalid verification format. Try /start again.")

            if verify_status and verify_status.get("verify_token") == token:
                await db.update_verify_status(user_id, is_verified=True, verified_time=time.time())
                return await message.reply(
                    f"✅ Token verified! Vᴀʟɪᴅ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}"
                )
            else:
                return await message.reply("⚠️ Invalid or expired token. Please /start again.")

    # 📁 Handle saved file sending
    data = await db.get_file(text)
    if not data:
        return await message.reply_text("❌ No files found for this key.")

    try:
        sent_msgs = []
        # Build metadata map if available
        meta_map = {}
        for meta in data.get("file_meta", []) or []:
            fid = meta.get("file_id")
            if fid:
                meta_map[fid] = meta
        for fid in data["file_ids"]:
            meta = meta_map.get(fid, {})
            mtype = meta.get("media_type")
            prev_caption = meta.get("caption") or ""
            filename = meta.get("file_name")
            caption = None
            if mtype == "document":
                if CUSTOM_CAPTION:
                    try:
                        caption = CUSTOM_CAPTION.format(previouscaption=prev_caption, filename=filename)
                    except Exception:
                        caption = CUSTOM_CAPTION
                else:
                    caption = prev_caption or None
            else:
                caption = prev_caption or None
            sent = await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=fid,
                caption=caption,
                parse_mode=ParseMode.HTML,
                protect_content=PROTECT_CONTENT
            )
            sent_msgs.append(sent)

        if FILE_AUTO_DELETE > 0:
            notify = await message.reply(
                f"<b><blockquote>This file(s) will be deleted in {get_exp_time(FILE_AUTO_DELETE)}.\n"
                f"Please save or forward them before they are removed.</blockquote></b>"
            )
            await asyncio.sleep(FILE_AUTO_DELETE)

            for s in sent_msgs:
                try:
                    await s.delete()
                except:
                    pass
            try:
                await notify.delete()
            except:
                pass

    except Exception as e:
        await message.reply_text(f"⚠️ Failed to send files:\n<code>{e}</code>")
