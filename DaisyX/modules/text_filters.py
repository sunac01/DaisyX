# This filte is ported from WilliamButcherBot
# Credits goes to TheHamkerCat

# Don't edit these lines

from pyrogram import filters

from DaisyX.db.mongo_helpers.filterdb import (
    delete_filter,
    get_filter,
    get_filters_names,
    save_filter,
)
from DaisyX.function.pluginhelpers import member_permissions
from DaisyX.services.pyrogram import pbot as app


@app.on_message(filters.command("f") & ~filters.edited & ~filters.private)
async def save_filters(_, message):
    if len(message.command) < 2 or not message.reply_to_message:
        await message.reply_text(
            "**Yalnızca Metin Ve Çıkartmada Çalışır**"
        )

    elif not message.reply_to_message.text and not message.reply_to_message.sticker:
        await message.reply_text(
            "__**Yalnıca Metin Ve Çıkartmada Çalışır**"
        )

    elif len(await member_permissions(message.chat.id, message.from_user.id)) < 1:
        await message.reply_text("**Yeterli izniniz yok**")
    elif not "can_change_info" in (
        await member_permissions(message.chat.id, message.from_user.id)
    ):
        await message.reply_text("**Yeterli izniniz yok**")
    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            await message.reply_text("**Kullanım**/filtre filtre adı")
            return
        _type = "text" if message.reply_to_message.text else "sticker"
        _filter = {
            "type": _type,
            "data": message.reply_to_message.text.markdown
            if _type == "text"
            else message.reply_to_message.sticker.file_id,
        }
        await save_filter(message.chat.id, name, _filter)
        await message.reply_text(f"__**{name} Filtresi Kaydedildi.**__")


@app.on_message(filters.command("fliste") & ~filters.edited & ~filters.private)
async def get_filterss(_, message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        return
    else:
        msg = f"Tüm Filtreler {message.chat.title}\n"
        for _filter in _filters:
            msg += f"**-** `{_filter}`\n"
        await message.reply_text(msg)


@app.on_message(filters.command("fsil") & ~filters.edited & ~filters.private)
async def del_filter(_, message):
    if len(message.command) < 2:
        await message.reply_text(
            "**Kullanım**/stop filtre adı"
        )

    elif len(await member_permissions(message.chat.id, message.from_user.id)) < 1:
        await message.reply_text("**Yeterli izniniz yok**")

    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            await message.reply_text(
                "**Kullanım**/stop filtre adı"
            )
            return
        chat_id = message.chat.id
        deleted = await delete_filter(chat_id, name)
        if deleted:
            await message.reply_text(f"**{name}**filtresi silindi.")
        else:
            await message.reply_text(f"**Böyle bir filtre yok.**")


@app.on_message(
    filters.incoming & filters.text & ~filters.private & ~filters.channel & ~filters.bot
)
async def filters_re(_, message):
    try:
        if message.text[0] != "/":
            text = message.text.lower().strip().split(" ")
            if text:
                chat_id = message.chat.id
                list_of_filters = await get_filters_names(chat_id)
                for word in text:
                    if word in list_of_filters:
                        _filter = await get_filter(chat_id, word)
                        data_type = _filter["type"]
                        data = _filter["data"]
                        if data_type == "text":
                            await message.reply_text(data)
                        else:
                            await message.reply_sticker(data)
                        message.continue_propagation()
    except Exception:
        pass
