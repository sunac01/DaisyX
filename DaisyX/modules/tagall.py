# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.


from pyrogram import filters

from DaisyX.function.pluginhelpers import admins_only, get_text
from DaisyX.services.pyrogram import pbot


@pbot.on_message(filters.command("toplan"))
@admins_only
async def tagall(client, message):
    await message.reply("`İşleniyorr.....`")
    sh = get_text(message)
    if not sh:
        sh = "Selam!"
    mentions = ""
    async for member in client.iter_chat_members(message.chat.id):
        mentions += member.user.mention + " "
    n = 4096
    kk = [mentions[i : i + n] for i in range(0, len(mentions), n)]
    for i in kk:
        j = f"<b>{sh}</b> \n{i}"
        await client.send_message(message.chat.id, j, parse_mode="html")
        

_mod_name_ = "Tagall"
_help_ = """
- /tagall : Tag everyone in a chat
"""
