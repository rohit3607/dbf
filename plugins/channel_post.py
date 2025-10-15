#(©)Codexbotz

import asyncio, sys, os, subprocess
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import encode, admin

@Bot.on_message(filters.private & admin & ~filters.command(['start', 'commands','users','broadcast','batch', 'custom_batch', 'genlink','stats', 'dlt_time', 'check_dlt_time', 'ban', 'unban', 'banlist', 'addchnl', 'delchnl', 'listchnl', 'fsub_mode', 'add_admin', 'deladmin', 'admins', 'delreq', 'cancel', 'setfile', 'listfile', 'delfile', 'update']))
async def channel_post(client: Client, message: Message):


    """reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)"""

@Bot.on_message(filters.command('update') & filters.private & admin)
async def update_bot(client, message):
    #if message.from_user.id != OWNER_ID:
        #return await message.reply_text("You are not authorized to update the bot.")

    try:
        msg = await message.reply_text("<b><blockquote>Pulling the latest updates and restarting the bot...</blockquote></b>")

        # Run git pull
        git_pull = subprocess.run(["git", "pull"], capture_output=True, text=True)

        if git_pull.returncode == 0:
            await msg.edit_text(f"<b><blockquote>Updates pulled successfully:\n\n{git_pull.stdout}</blockquote></b>")
        else:
            await msg.edit_text(f"<b><blockquote>Failed to pull updates:\n\n{git_pull.stderr}</blockquote></b>")
            return

        await asyncio.sleep(3)

        await msg.edit_text("<b><blockquote>✅ Bᴏᴛ ɪs ʀᴇsᴛᴀʀᴛɪɴɢ ɴᴏᴡ...</blockquote></b>")

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
        return

    finally:
        os.execl(sys.executable, sys.executable, *sys.argv)
