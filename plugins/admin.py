import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import *



# Commands for adding admins by owner
@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    check = 0
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>You need to provide user ID(s) to add as admin.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/add_admin [user_id]</code> — Add one or more user IDs\n\n"
            "<b>Example:</b>\n"
            "<code>/add_admin 1234567890 9876543210</code>",
            reply_markup=reply_markup
        )

    admin_list = ""
    valid_ids = []
    for id in admins:
        try:
            id_int = int(id)
        except:
            admin_list += f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n"
            continue

        if id_int in admin_ids:
            admin_list += f"<blockquote><b>ID <code>{id}</code> already exists.</b></blockquote>\n"
            continue

        valid_ids.append(id_int)
        admin_list += f"<b><blockquote>(ID: <code>{id}</code>) added.</blockquote></b>\n"
        check += 1

    if check == len(valid_ids):
        for id in valid_ids:
            await db.add_admin(id)
        await pro.edit(f"<b>✅ Admin(s) added successfully:</b>\n\n{admin_list}", reply_markup=reply_markup)
    else:
        await pro.edit(
            f"<b>⚠️ Some IDs were not added:</b>\n\n{admin_list.strip()}\n\n"
            "<b><i>Check input and try again.</i></b>",
            reply_markup=reply_markup
        )


@Bot.on_message(filters.command('deladmin') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>Please provide valid admin ID(s) to remove.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/deladmin [user_id]</code> — Remove specific IDs\n"
            "<code>/deladmin all</code> — Remove all admins",
            reply_markup=reply_markup
        )

    if len(admins) == 1 and admins[0].lower() == "all":
        if admin_ids:
            for id in admin_ids:
                await db.del_admin(id)
            ids = "\n".join(f"<blockquote><code>{admin}</code> ✅</blockquote>" for admin in admin_ids)
            return await pro.edit(f"<b>⛔️ All admin IDs have been removed:</b>\n{ids}", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>No admin IDs to remove.</blockquote></b>", reply_markup=reply_markup)

    if admin_ids:
        passed = ''
        for admin_id in admins:
            try:
                id = int(admin_id)
            except:
                passed += f"<blockquote><b>Invalid ID: <code>{admin_id}</code></b></blockquote>\n"
                continue

            if id in admin_ids:
                await db.del_admin(id)
                passed += f"<blockquote><code>{id}</code> ✅ Removed</blockquote>\n"
            else:
                passed += f"<blockquote><b>ID <code>{id}</code> not found in admin list.</b></blockquote>\n"

        await pro.edit(f"<b>⛔️ Admin removal result:</b>\n\n{passed}", reply_markup=reply_markup)
    else:
        await pro.edit("<b><blockquote>No admin IDs available to delete.</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & filters.private & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()

    if not admin_ids:
        admin_list = "<b><blockquote>❌ No admins found.</blockquote></b>"
    else:
        admin_list = "\n".join(f"<b><blockquote>ID: <code>{id}</code></blockquote></b>" for id in admin_ids)

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
    await pro.edit(f"<b>⚡ Current Admin List:</b>\n\n{admin_list}", reply_markup=reply_markup)

import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *

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

#Request force sub mode commad,,,,,,
@Bot.on_message(filters.command('fsub_mode') & filters.private & admin)
async def change_force_sub_mode(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>", quote=True)
    channels = await db.show_channels()

    if not channels:
        return await temp.edit("<b>❌ No force-sub channels found.</b>")

    buttons = []
    for ch_id in channels:
        try:
            chat = await client.get_chat(ch_id)
            mode = await db.get_channel_mode(ch_id)
            status = "🟢" if mode == "on" else "🔴"
            title = f"{status} {chat.title}"
            buttons.append([InlineKeyboardButton(title, callback_data=f"rfs_ch_{ch_id}")])
        except:
            buttons.append([InlineKeyboardButton(f"⚠️ {ch_id} (Unavailable)", callback_data=f"rfs_ch_{ch_id}")])

    buttons.append([InlineKeyboardButton("Close ✖️", callback_data="close")])

    await temp.edit(
        "<b>⚡ Select a channel to toggle Force-Sub Mode:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

# This handler captures membership updates (like when a user leaves, banned)
@Bot.on_chat_member_updated()
async def handle_Chatmembers(client, chat_member_updated: ChatMemberUpdated):    
    chat_id = chat_member_updated.chat.id

    if await db.reqChannel_exist(chat_id):
        old_member = chat_member_updated.old_chat_member

        if not old_member:
            return

        if old_member.status == ChatMemberStatus.MEMBER:
            user_id = old_member.user.id

            if await db.req_user_exist(chat_id, user_id):
                await db.del_req_user(chat_id, user_id)


# This handler will capture any join request to the channel/group where the bot is an admin
@Bot.on_chat_join_request()
async def handle_join_request(client, chat_join_request):
    chat_id = chat_join_request.chat.id
    user_id = chat_join_request.from_user.id

    #print(f"[JOIN REQUEST] User {user_id} sent join request to {chat_id}")

    # Print the result of db.reqChannel_exist to check if the channel exists
    channel_exists = await db.reqChannel_exist(chat_id)
    #print(f"Channel {chat_id} exists in the database: {channel_exists}")

    if channel_exists:
        if not await db.req_user_exist(chat_id, user_id):
            await db.req_user(chat_id, user_id)
            #print(f"Added user {user_id} to request list for {chat_id}")

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

# Add channel
@Bot.on_message(filters.command('addchnl') & filters.private & admin)
async def add_force_sub(client: Client, message: Message):
    temp = await message.reply("Wait a sec...", quote=True)
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        return await temp.edit(
            "Usage:\n<code>/addchnl -100xxxxxxxxxx</code>"
        )

    try:
        chat_id = int(args[1])
    except ValueError:
        return await temp.edit("❌ Invalid chat ID!")

    all_chats = await db.show_channels()
    if chat_id in [c if isinstance(c, int) else c[0] for c in all_chats]:
        return await temp.edit(f"Already exists:\n<code>{chat_id}</code>")

    try:
        chat = await client.get_chat(chat_id)
        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            return await temp.edit("❌ Only channels/supergroups allowed.")

        bot_member = await client.get_chat_member(chat.id, "me")
        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await temp.edit("❌ Bot must be admin in that chat.")

        # Try to get invite link
        try:
            link = await client.export_chat_invite_link(chat.id)
        except Exception:
            link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}"

        await db.add_channel(chat_id)
        return await temp.edit(
            f"✅ Added Successfully!\n\n"
            f"<b>Name:</b> <a href='{link}'>{chat.title}</a>\n"
            f"<b>ID:</b> <code>{chat_id}</code>",
            disable_web_page_preview=True
        )

    except Exception as e:
        return await temp.edit(f"❌ Failed to add chat:\n<code>{chat_id}</code>\n\n<i>{e}</i>")


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

# Delete channel
@Bot.on_message(filters.command('delchnl') & filters.private & admin)
async def del_force_sub(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>", quote=True)
    args = message.text.split(maxsplit=1)
    all_channels = await db.show_channels()

    if len(args) != 2:
        return await temp.edit("<b>Usage:</b> <code>/delchnl <channel_id | all></code>")

    if args[1].lower() == "all":
        if not all_channels:
            return await temp.edit("<b>❌ No force-sub channels found.</b>")
        for ch_id in all_channels:
            await db.del_channel(ch_id)
        return await temp.edit("<b>✅ All force-sub channels have been removed.</b>")

    try:
        ch_id = int(args[1])
    except ValueError:
        return await temp.edit("<b>❌ Invalid Channel ID</b>")

    if ch_id in all_channels:
        await db.rem_channel(ch_id)
        return await temp.edit(f"<b>✅ Channel removed:</b> <code>{ch_id}</code>")
    else:
        return await temp.edit(f"<b>❌ Channel not found in force-sub list:</b> <code>{ch_id}</code>")

# View all channels
@Bot.on_message(filters.command('listchnl') & filters.private & admin)
async def list_force_sub_channels(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>", quote=True)
    channels = await db.show_channels()

    if not channels:
        return await temp.edit("<b>❌ No force-sub channels found.</b>")

    result = "<b>⚡ Force-sub Channels:</b>\n\n"
    for ch_id in channels:
        try:
            chat = await client.get_chat(ch_id)
            link = chat.invite_link or await client.export_chat_invite_link(chat.id)
            result += f"<b>•</b> <a href='{link}'>{chat.title}</a> [<code>{ch_id}</code>]\n"
        except Exception:
            result += f"<b>•</b> <code>{ch_id}</code> — <i>Unavailable</i>\n"

    await temp.edit(result, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]]))

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

@Bot.on_message(filters.command('delreq') & filters.private & admin)
async def delete_requested_users(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usᴀɢᴇ: `/delreq <channel_id>`", quote=True)

    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID.", quote=True)

    # Get channel request data
    channel_data = await db.rqst_fsub_Channel_data.find_one({'_id': channel_id})
    if not channel_data:
        return await message.reply("ℹ️ Nᴏ ʀᴇǫᴜᴇsᴛ ᴄʜᴀɴɴᴇʟ ғᴏᴜɴᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀɴɴᴇʟ.", quote=True)

    user_ids = channel_data.get("user_ids", [])
    if not user_ids:
        return await message.reply("✅ Nᴏ ᴜsᴇʀs ᴛᴏ ᴘʀᴏᴄᴇss.", quote=True)

    removed = 0
    skipped = 0
    left_users = 0

    for user_id in user_ids:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ):
                skipped += 1  # Still a participant, and in req list
                continue
            else:
                await db.del_req_user(channel_id, user_id)
                left_users += 1
        except UserNotParticipant:
            await db.del_req_user(channel_id, user_id)
            left_users += 1
        except Exception as e:
            print(f"[!] Error checking user {user_id}: {e}")
            skipped += 1

    for user_id in user_ids:
        if not await db.req_user_exist(channel_id, user_id):
            await db.del_req_user(channel_id, user_id)
            removed += 1

    return await message.reply(
        f"✅ Cʟᴇᴀɴᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ᴄʜᴀɴɴᴇʟ `{channel_id}`\n\n"
        f"👤 Rᴇᴍᴏᴠᴇᴅ ᴜsᴇʀs ɴᴏᴛ ɪɴ ᴄʜᴀɴɴᴇʟ: `{left_users}`\n"
        f"🗑️ Rᴇᴍᴏᴠᴇᴅ ʟᴇғᴛᴏᴠᴇʀ ɴᴏɴ-ʀᴇǫᴜᴇsᴛ ᴜsᴇʀs: `{removed}`\n"
        f"✅ Sᴛɪʟʟ ᴍᴇᴍʙᴇʀs: `{skipped}`",
        quote=True
    )
