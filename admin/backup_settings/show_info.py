from telegram import Update, Chat
from telegram.ext import ContextTypes, CommandHandler
from custom_filters import Admin
from admin.backup_settings.common import set_channel_commands


async def show_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        text = ""
        for channel in set_channel_commands:
            text += f"{channel.replace("set_default_", "")}: <code>{context.bot_data.get(channel, 'غير محدد بعد')}</code>\n"
        await update.message.reply_text(text=text)


async def show_texts_need_to_change(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get("texts_need_to_change", False):
            context.bot_data["texts_need_to_change"] = {}
            await update.message.reply_text(
                text="ليس لديك نصوص لتغييرها بعد ❗️"
            )
            return
        text = "النصوص التي يجب تغييرها:\n"
        for change_from, change_to in context.bot_data[
            "texts_need_to_change"
        ].items():
            text += f"<code>{change_from} -> {change_to}</code>\n"
        await update.message.reply_text(text=text)


show_channels_command = CommandHandler("show_channels", show_channels)
show_texts_need_to_change_command = CommandHandler("show_texts_need_to_change", show_texts_need_to_change)
