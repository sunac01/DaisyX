from io import BytesIO
from traceback import format_exc

from pyrogram import filters
from pyrogram.types import Message

from DaisyX.services.pyrogram import pbot as app
from DaisyX.function.pluginhelpers import capture_err
from DaisyX.function.inlinehelper import arq

async def quotify(messages: list):
    response = await arq.quotly(messages)
    if not response.ok:
        return [False, response.result]
    sticker = response.result
    sticker = BytesIO(sticker)
    sticker.name = "sticker.webp"
    return [True, sticker]


def getArg(message: Message) -> str:
    arg = message.text.strip().split(None, 1)[1].strip()
    return arg


def isArgInt(message: Message) -> bool:
    count = getArg(message)
    try:
        count = int(count)
        return [True, count]
    except ValueError:
        return [False, 0]


@app.on_message(filters.command("q"))
async def quotly_func(_, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Alıntı yapmak için bir mesaja cevap verin.")
        return
    if not message.reply_to_message.text:
        await message.reply_text(
            "Cevaplanan mesajın metni yok, alıntı yapılamaz."
        )
        return
    m = await message.reply_text("Çıkartma Gönderiliyor")
    if len(message.command) < 2:
        messages = [message.reply_to_message]

    elif len(message.command) == 2:
        arg = isArgInt(message)
        if arg[0]:
            if arg[1] < 2 or arg[1] > 10:
                await m.edit("Argüman 2-10 arasında olmalıdır.")
                return
            count = arg[1]
            messages = await app.get_messages(
                message.chat.id,
                [
                    i
                    for i in range(
                        message.reply_to_message.message_id,
                        message.reply_to_message.message_id + count,
                    )
                ],
                replies=0,
            )
        else:
            if getArg(message) != "r":
                await m.edit(
                    "Yanlış Argüman, Pass 'r' or 'INT', EX: /q 2"
                )
                return
            reply_message = await app.get_messages(
                message.chat.id,
                message.reply_to_message.message_id,
                replies=1,
            )
            messages = [reply_message]
    else:
        await m.edit(
            "Yanlış argüman"
        )
        return
    try:
        sticker = await quotify(messages)
        if not sticker[0]:
            await message.rely_text(sticker[1])
            await m.delete()
            return
        sticker = sticker[1]
        await message.reply_sticker(sticker)
        await m.delete()
        sticker.close()
    except Exception as e:
        await message.reply_text(
            "Mesajlardan alıntı yapılırken bir hata oldu,"
            + " Bu hata genellikle bir "
            + " metni olmayan bir alıntıdır "
        )
        await m.delete()
        e = format_exc()
        print(e)
        return
