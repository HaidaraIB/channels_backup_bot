from telegram import Update, Chat, BotCommandScopeChat
from telegram.ext import CommandHandler, ContextTypes, Application, ConversationHandler
import os
import models
from custom_filters import Admin
from common.decorators import check_if_user_banned_dec, add_new_user_dec
from common.keyboards import build_admin_keyboard
from common.common import check_hidden_keyboard


async def inits(app: Application):
    await models.Admin.add_new_admin(admin_id=int(os.getenv("OWNER_ID")))


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st_cmd = ("start", "start command")
    commands = [st_cmd]
    if Admin().filter(update):
        commands.append(("admin", "admin command"))
        commands.append(("show_texts_need_to_change", "show texts need to change"))
        commands.append(("show_channels", "show channels"))
        commands.append(("set_text_need_to_change", "set text need to change"))
        commands.append(("cancel_backup", "cancel backup"))
        commands.append(("start_backup", "start backup"))
        commands.append(("cancel", "cancel"))
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
        for channel_command in set_channel_commands:
            commands.append(
                (
                    channel_command,
                    channel_command.replace("/", "").replace("_", " "),
                )
            )
    await context.bot.set_my_commands(
        commands=commands, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )


@add_new_user_dec
@check_if_user_banned_dec
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await set_commands(update, context)
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await set_commands(update, context)
        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=check_hidden_keyboard(context),
        )

        await update.message.reply_text(
            text="تعمل الآن كآدمن 🕹",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
