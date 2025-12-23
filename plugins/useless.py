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

    # Collect file ids from the received message
    file_ids = _extract_file_ids(user_msg)

    # If this message is part of a media group, try to collect the rest of the group
    if user_msg.media_group_id:
        mgid = user_msg.media_group_id
        # allow a short window to receive rest of the group (they usually arrive quickly)
        while True:
            try:
                more = await client.ask(chat_id=message.chat.id, text="Waiting for rest of media group...", timeout=1)
            except asyncio.TimeoutError:
                break
            if more.text and more.text.strip().upper() == "STOP":
                break
            # include items that belong to the same media_group
            if getattr(more, "media_group_id", None) == mgid and more.from_user.id == user_msg.from_user.id:
                file_ids.extend(_extract_file_ids(more))
            else:
                # if it's a different message, ignore it (user can re-send if needed)
                continue

    await message.reply("✅ Collection finished.", reply_markup=ReplyKeyboardRemove())

    if not file_ids:
        return await message.reply("❌ No valid media message was received and stored.")

    for fid in file_ids:
        await db.add_file_to_key(key, message.chat.id, fid)

    await message.reply(f"✅ Stored {len(file_ids)} file(s) under key `{key}` successfully.")


# =========================
# /setfiles Command (Batch collection for a duration)
# =========================
@Bot.on_message(filters.command("setfiles") & filters.private & admin)
async def set_files_batch(client: Bot, message: Message):
    """Collect multiple files from the user for a specified duration (default 60s).

    Usage: /setfiles <number> [seconds]
    Example: /setfiles 123 60  (collect files for 60 seconds)
    """
    if len(message.command) not in (2, 3):
        return await message.reply_text("⚠️ Usage:\n`/setfiles <number> [seconds]`\nExample: /setfiles 123 60")

    key = message.command[1].strip()
    if not key.isdigit():
        return await message.reply_text("❌ Only numbers are allowed as keys.")

    duration = 60
    if len(message.command) == 3:
        try:
            duration = int(message.command[2])
            if duration <= 0:
                raise ValueError
        except Exception:
            return await message.reply_text("❌ Invalid duration. Provide time in seconds as a positive integer.")

    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)

    await message.reply(
        f"📥 Send all files/media you want to include under key `{key}` within {duration} seconds.\n\nPress STOP to finish early.",
        reply_markup=STOP_KEYBOARD
    )

    end_time = time.time() + duration
    while True:
        remaining = end_time - time.time()
        if remaining <= 0:
            break
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text=f"Waiting for media... ({int(remaining)}s left)",
                timeout=remaining
            )
        except asyncio.TimeoutError:
            break

        if user_msg.text and user_msg.text.strip().upper() == "STOP":
            break

        # Extract file ids (supports media groups by capturing each message)
        file_ids = _extract_file_ids(user_msg)
        finish_early = False

        # If this message is part of a media group, try to collect the rest of the group
        if user_msg.media_group_id:
            mgid = user_msg.media_group_id
            # allow a short window to receive rest of the group (they usually arrive quickly)
            while True:
                try:
                    more = await client.ask(chat_id=message.chat.id, text="Waiting for rest of media group...", timeout=1)
                except asyncio.TimeoutError:
                    break
                if more.text and more.text.strip().upper() == "STOP":
                    finish_early = True
                    break
                # include items that belong to the same media_group
                if getattr(more, "media_group_id", None) == mgid and more.from_user.id == user_msg.from_user.id:
                    file_ids.extend(_extract_file_ids(more))
                else:
                    # if it's a different message, ignore it (user can re-send if needed)
                    continue

        if not file_ids:
            await message.reply("❌ Unsupported message type, ignored.")
            if finish_early:
                break
            continue

        for fid in file_ids:
            collected.append((message.chat.id, fid))

        await message.reply(f"✅ Added ({len(collected)} total)")

        if finish_early:
            break

    await message.reply("✅ Collection finished.", reply_markup=ReplyKeyboardRemove())

    if not collected:
        return await message.reply("❌ No valid media messages were added.")

    # Store all collected file_ids under key
    for chat_id, fid in collected:
        await db.add_file_to_key(key, chat_id, fid)

    await message.reply(f"✅ All {len(collected)} files stored under key `{key}` successfully.")

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
        for fid in data["file_ids"]:
            sent = await client.send_cached_media(chat_id=message.chat.id, file_id=fid)
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
