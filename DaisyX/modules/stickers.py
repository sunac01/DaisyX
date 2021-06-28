# Copyright (C) 2021 TeamDaisyX


# This file is part of Daisy (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import io
import math
import os
from io import BytesIO

import requests
from aiogram.types.input_file import InputFile
from bs4 import BeautifulSoup as bs
from PIL import Image
from pyrogram import filters
from telethon import *
from telethon.errors.rpcerrorlist import StickersetInvalidError
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeSticker,
    InputStickerSetID,
    InputStickerSetShortName,
    MessageMediaPhoto,
)

from DaisyX import bot
from DaisyX.decorator import register
from DaisyX.services.events import register as Daisy
from DaisyX.services.pyrogram import pbot
from DaisyX.services.telethon import tbot
from DaisyX.services.telethonuserbot import ubot

from .utils.disable import disableable_dec
from .utils.language import get_strings_dec


def is_it_animated_sticker(message):
    try:
        if message.media and message.media.document:
            mime_type = message.media.document.mime_type
            if "tgsticker" in mime_type:
                return True
            return False
        return False
    except BaseException:
        return False


def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False


async def silently_send_message(conv, text):
    await conv.send_message(text)
    response = await conv.get_response()
    await conv.mark_read(message=response)
    return response


async def stickerset_exists(conv, setname):
    try:
        await tbot(GetStickerSetRequest(InputStickerSetShortName(setname)))
        response = await silently_send_message(conv, "/addsticker")
        if response.text == "Invalid pack selected.":
            await silently_send_message(conv, "/cancel")
            return False
        await silently_send_message(conv, "/cancel")
        return True
    except StickersetInvalidError:
        return False


def resize_image(image, save_locaton):
    """Copyright Rhyse Simpson:
    https://github.com/skittles9823/SkittBot/blob/master/tg_bot/modules/stickers.py
    """
    im = Image.open(image)
    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(maxsize)
    im.save(save_locaton, "PNG")


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


@Daisy(pattern="^/searchsticker (.*)")
async def _(event):
    input_str = event.pattern_match.group(1)
    combot_stickers_url = "https://combot.org/telegram/stickers?q="
    text = requests.get(combot_stickers_url + input_str)
    soup = bs(text.text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        await event.reply("No results found :(")
        return
    reply = f"Stickers Related to **{input_str}**:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\nâ€¢ [{title.get_text()}]({link})"
    await event.reply(reply)


@Daisy(pattern="^/packinfo$")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return

    if not event.is_reply:
        await event.reply("Reply to any sticker to get it's pack info.")
        return
    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await event.reply("Reply to any sticker to get it's pack info.")
        return
    stickerset_attr_s = rep_msg.document.attributes
    stickerset_attr = find_instance(stickerset_attr_s, DocumentAttributeSticker)
    if not stickerset_attr.stickerset:
        await event.reply("sticker does not belong to a pack.")
        return
    get_stickerset = await tbot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    await event.reply(
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Stickers In Pack:** `{len(get_stickerset.packs)}`\n"
        f"**Emojis In Pack:** {' '.join(pack_emojis)}"
    )


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


DEFAULTUSER = "DaisyX"
FILLED_UP_DADDY = "Invalid pack selected."


async def get_sticker_emoji(event):
    reply_message = await event.get_reply_message()
    try:
        final_emoji = reply_message.media.document.attributes[1].alt
    except:
        final_emoji = "😺"
    return final_emoji


@app.on_message(filters.command("kang") & ~filters.edited)
async def kang(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a sticker/image to kang it."
        )
    if not message.from_user:
        return await message.reply_text(
            "You are anon admin, kang stickers in my pm."
        )
    msg = await message.reply_text("Kanging Sticker..")

    # Find the proper emoji
    args = message.text.split()
    if len(args) > 1:
        sticker_emoji = str(args[1])
    elif (
        message.reply_to_message.sticker
        and message.reply_to_message.sticker.emoji
    ):
        sticker_emoji = message.reply_to_message.sticker.emoji
    else:
        sticker_emoji = "🤔"

    # Get the corresponding fileid, resize the file if necessary
    doc = (
        message.reply_to_message.photo
        or message.reply_to_message.document
    )
    try:
        if message.reply_to_message.sticker:
            sticker = await create_sticker(
                await get_document_from_file_id(
                    message.reply_to_message.sticker.file_id
                ),
                sticker_emoji,
            )
        elif doc:
            temp_file_path = await app.download_media(doc)
            image_type = imghdr.what(temp_file_path)
            if image_type not in SUPPORTED_TYPES:
                return await msg.edit(
                    "Format not supported! ({})".format(image_type)
                )
            try:
                temp_file_path = await resize_file_to_sticker_size(
                    temp_file_path
                )
            except OSError as e:
                await msg.edit_text("Something wrong happened.")
                raise Exception(
                    f"Something went wrong while resizing the sticker (at {temp_file_path}); {e}"
                )
                return False
            sticker = await create_sticker(
                await upload_document(
                    client, temp_file_path, message.chat.id
                ),
                sticker_emoji,
            )
            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)
        else:
            return await msg.edit("Nope, can't kang that.")
    except ShortnameOccupyFailed:
        await message.reply_text("Change Your Name Or Username")
        return

    except Exception as e:
        await message.reply_text(str(e))
        e = format_exc()
        return print(e)

    # Find an available pack & add the sticker to the pack; create a new pack if needed
    # Would be a good idea to cache the number instead of searching it every single time...
    packnum = 0
    packname = "f" + str(message.from_user.id) + "_by_" + BOT_USERNAME
    try:
        while True:
            stickerset = await get_sticker_set_by_name(
                client, packname
            )
            if not stickerset:
                stickerset = await create_sticker_set(
                    client,
                    message.from_user.id,
                    f"{message.from_user.first_name[:32]}'s kang pack",
                    packname,
                    [sticker],
                )
            elif stickerset.set.count >= MAX_STICKERS:
                packnum += 1
                packname = (
                    "f"
                    + str(packnum)
                    + "_"
                    + str(message.from_user.id)
                    + "_by_"
                    + BOT_USERNAME
                )
                continue
            else:
                await add_sticker_to_set(client, stickerset, sticker)
            break

        await msg.edit(
            "Sticker Kanged To [Pack](t.me/addstickers/{})\nEmoji: {}".format(
                packname, sticker_emoji
            )
        )
    except (PeerIdInvalid, UserIsBlocked):
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Start", url=f"t.me/{BOT_USERNAME}"
                    )
                ]
            ]
        )
        await msg.edit(
            "You Need To Start A Private Chat With Me.",
            reply_markup=keyboard,
        )
    except StickerPngNopng:
        await message.reply_text(
            "Stickers must be png files but the provided image was not a png"
        )
    except StickerPngDimensions:
        await message.reply_text(
            "The sticker png dimensions are invalid."
        )


@Daisy(pattern="^/kaldir$")
async def _(event):
    try:
        if not event.is_reply:
            await event.reply(
                "Kişisel çıkartma paketinizden çıkarmak için bir çıkartmayı yanıtlayın."
            )
            return
        reply_message = await event.get_reply_message()
        kanga = await event.reply("`Siliniyor .`")

        if not is_message_image(reply_message):
            await kanga.edit("Lütfen bir çıkartmayı yanıtlayın")
            return

        rmsticker = await ubot.get_messages(event.chat_id, ids=reply_message.id)

        stickerset_attr_s = reply_message.document.attributes
        stickerset_attr = find_instance(stickerset_attr_s, DocumentAttributeSticker)
        if not stickerset_attr.stickerset:
            await event.reply("Etiket bir pakete ait değildir.")
            return

        get_stickerset = await tbot(
            GetStickerSetRequest(
                InputStickerSetID(
                    id=stickerset_attr.stickerset.id,
                    access_hash=stickerset_attr.stickerset.access_hash,
                )
            )
        )

        packname = get_stickerset.set.short_name

        sresult = (
            await ubot(
                functions.messages.GetStickerSetRequest(
                    InputStickerSetShortName(packname)
                )
            )
        ).documents
        for c in sresult:
            if int(c.id) == int(stickerset_attr.stickerset.id):
                pass
            else:
                await kanga.edit(
                    "Bu çıkartma, kişisel çıkartma paketinizden zaten kaldırıldı."
                )
                return

        await kanga.edit("`Siiniyor ..`")

        async with ubot.conversation("@Stickers") as bot_conv:

            await silently_send_message(bot_conv, "/cancel")
            response = await silently_send_message(bot_conv, "/delsticker")
            if "Choose" not in response.text:
                await tbot.edit_message(
                    kanga, f"**Başarısız oldu**! @Stickers replied: {response.text}"
                )
                return
            response = await silently_send_message(bot_conv, packname)
            if not response.text.startswith("Please"):
                await tbot.edit_message(
                    kanga, f"**Başarısız oldu**! @Stickers replied: {response.text}"
                )
                return
            try:
                await rmsticker.forward_to("@Stickers")
            except Exception as e:
                print(e)
            if response.text.startswith("Sadece Bu Pakette"):
                await silently_send_message(bot_conv, "Yine de Sil")

            await kanga.edit("`Siliniyor ...`")
            response = await bot_conv.get_response()
            if not "Sildim" in response.text:
                await tbot.edit_message(
                    kanga, f"**Başarısız oldu**! @Stickers replied: {response.text}"
                )
                return

            await kanga.edit(
                "Bu çıkartma kişisel paketinizden başarıyla silindi.."
            )
    except Exception as e:
        os.remove("sticker.webp")
        print(e)


@register(cmds="getsticker")
@disableable_dec("getsticker")
@get_strings_dec("stickers")
async def get_sticker(message, strings):
    if "reply_to_message" not in message or "sticker" not in message.reply_to_message:
        await message.reply(strings["rpl_to_sticker"])
        return

    sticker = message.reply_to_message.sticker
    file_id = sticker.file_id
    text = strings["ur_sticker"].format(emoji=sticker.emoji, id=file_id)

    sticker_file = await bot.download_file_by_id(file_id, io.BytesIO())

    await message.reply_document(
        InputFile(
            sticker_file, filename=f"{sticker.set_name}_{sticker.file_id[:5]}.png"
        ),
        text,
    )


@pbot.on_message(filters.command("sticker_id") & ~filters.edited)
async def sticker_id(_, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a sticker.")
        return
    if not message.reply_to_message.sticker:
        await message.reply_text("Reply to a sticker.")
        return
    file_id = message.reply_to_message.sticker.file_id
    await message.reply_text(f"`{file_id}`")


__mod_name__ = "Stickers"

__help__ = """
Stickers are the best way to show emotion.

<b>Available commands:</b>
- /searchsticker: Search stickers for given query.
- /packinfo: Reply to a sticker to get it's pack info
- /getsticker: Uploads the .png of the sticker you've replied to
- /sticker_id : Reply to Sticker for getting sticker Id. 
- /kang [Emoji for sticker] [reply to Image/Sticker]: Kang replied sticker/image.
- /rmkang [REPLY]: Remove replied sticker from your kang pack.
"""
