from telegram import InlineKeyboardButton
from telegram.ext import ContextTypes
from TeleClientSingleton import TeleClientSingleton
from telethon.tl.patched import Message
import asyncio

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
    async for msg in tele_client.client.iter_messages(entity=vip_channel):
        msg: Message = msg
        if context.bot_data["running_backups"].get(vip_channel, False):
            for change_from, change_to in context.bot_data[
                "texts_need_to_change"
            ].items():
                msg.text = msg.text.replace(change_from, change_to)
            await tele_client.client.send_message(entity=backup_channel, message=msg)
            await asyncio.sleep(5)
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
