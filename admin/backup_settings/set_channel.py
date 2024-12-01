from telegram import Update, Chat
from telegram.ext import ContextTypes, CommandHandler
from custom_filters import Admin
from admin.backup_settings.common import set_channel_commands
import models


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
        channel_id = int(context.args[0])
        channel = update.message.text.split(" ")[0].replace("/", "")
        context.bot_data[channel] = channel_id

        if "vip" in channel and context.bot_data.get(
            channel.replace("vip", "backup"), False
        ):
            await models.BackupChannel.add(
                channel_id=context.bot_data[channel.replace("vip", "backup")],
                from_channel_id=channel_id,
            )
        elif "backup" in channel and context.bot_data.get(
            channel.replace("backup", "vip"), False
        ):
            await models.BackupChannel.add(
                channel_id=channel_id,
                from_channel_id=context.bot_data[channel.replace("backup", "vip")],
            )
            
        await update.message.reply_text(text="تمت العملية بنجاح ✅")


set_channel_commands = CommandHandler(
    set_channel_commands,
    set_channel,
)
