from telegram import InlineKeyboardButton
from telegram.ext import ContextTypes
from telethon import errors, TelegramClient
from TeleClientSingleton import TeleClientSingleton
from telethon.tl.patched import Message
from common.error_handler import write_error
import asyncio
import traceback


set_channel_commands = [
    "set_default_vip1",
    "set_default_vip2",
    "set_default_vip3",
    "set_default_vip4",
    "set_default_backup1",
    "set_default_backup2",
    "set_default_backup3",
    "set_default_backup4",
]

set_vip_channel_commands = [
    "set_default_vip1",
    "set_default_vip2",
    "set_default_vip3",
    "set_default_vip4",
]
set_backup_channel_commands = [
    "set_default_backup1",
    "set_default_backup2",
    "set_default_backup3",
    "set_default_backup4",
]


def build_channels_keyboard(channels):
    keyboard = []
    for i in range(0, len(channels), 2):
        row = [
            InlineKeyboardButton(
                text=str(channels[i]),
                callback_data=str(channels[i]),
            )
        ]
        if i + 1 != len(channels):
            row.append(
                InlineKeyboardButton(
                    text=str(channels[i + 1]),
                    callback_data=str(channels[i + 1]),
                )
            )
        keyboard.append(row)
    return keyboard


async def perform_backup(
    vip_channel: int,
    backup_channel: int,
    context: ContextTypes.DEFAULT_TYPE,
    admin_id: int,
):
    tele_client = TeleClientSingleton()
    if not context.bot_data.get("texts_need_to_change", False):
        context.bot_data["texts_need_to_change"] = {}

    current_grouped_id = 0
    gallery = []

    async for msg in tele_client.client.iter_messages(
        entity=vip_channel,
        reverse=True,
    ):
        if not isinstance(msg, Message):
            continue
        msg: Message = msg
        if context.bot_data["running_backups"].get(vip_channel, False):
            for change_from, change_to in context.bot_data[
                "texts_need_to_change"
            ].items():
                if msg.text:
                    msg.text = msg.text.replace(change_from, change_to)

            if not msg.grouped_id:
                if gallery:
                    await backup_album(
                        client=tele_client.client,
                        entity=backup_channel,
                        album=gallery,
                    )
                    sleep_time = 5 * len(gallery)
                    gallery = []
                    current_grouped_id = 0
                    await asyncio.sleep(sleep_time)
                await backup_message(
                    client=tele_client.client,
                    entity=backup_channel,
                    message=msg,
                )
                await asyncio.sleep(5)
            else:
                if current_grouped_id != 0 and msg.grouped_id != current_grouped_id:
                    gallery.append(msg)
                    await backup_album(
                        client=tele_client.client,
                        entity=backup_channel,
                        album=gallery,
                    )
                    sleep_time = 5 * len(gallery)
                    gallery = []
                    current_grouped_id = msg.grouped_id
                    await asyncio.sleep(sleep_time)
                else:
                    gallery.append(msg)
                    current_grouped_id = msg.grouped_id
        else:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"تم إلغاء عملية النسخ\n"
                    f"<code>{vip_channel} -> {backup_channel}</code>\n"
                    "بنجاح ✅"
                ),
            )
            return
    await context.bot.send_message(
        chat_id=admin_id,
        text=(
            f"تمت عملية النسخ\n"
            f"<code>{vip_channel} -> {backup_channel}</code>\n"
            "بنجاح ✅"
        ),
    )


async def backup_album(client: TelegramClient, entity, album):
    try:
        await client.send_file(
            entity=entity,
            file=album,
            caption=[m.text for m in album],
        )
    except errors.rpcerrorlist.FloodWaitError as f:
        await asyncio.sleep(f.seconds + 5)
        await client.send_file(
            entity=entity,
            file=album,
            caption=[m.text for m in album],
        )
    except Exception as e:
        tb_list = traceback.format_exception(None, e, e.__traceback__)
        tb_string = "".join(tb_list)
        write_error(tb_string + "\n\n")


async def backup_message(client: TelegramClient, entity, message):
    try:
        await client.send_message(
            entity=entity,
            message=message,
        )
    except errors.rpcerrorlist.FloodWaitError as f:
        await asyncio.sleep(f.seconds + 5)
        await client.send_message(
            entity=entity,
            message=message,
        )
    except Exception as e:
        tb_list = traceback.format_exception(None, e, e.__traceback__)
        tb_string = "".join(tb_list)
        write_error(tb_string + "\n\n")
