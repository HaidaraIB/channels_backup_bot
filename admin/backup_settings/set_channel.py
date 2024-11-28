from telegram import Update, Chat
from telegram.ext import ContextTypes, CommandHandler
from custom_filters import Admin
from admin.backup_settings.common import set_channel_commands


async def set_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.args:
            await update.message.reply_text(
                text=(
                    f"الرجاء تحديد id القناة الهدف، مثال:"
                    f"\n{update.message.text} 12345"
                )
            )
            return
        channel = update.message.text.split(" ")[0].replace("/", "")
        context.bot_data[channel] = context.args[0]
        await update.message.reply_text(text="تمت العملية بنجاح ✅")


set_channel_commands = CommandHandler(
    set_channel_commands,
    set_channel,
)
