from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from custom_filters import Admin
from common.keyboards import build_confirmation_keyboard

RUNNING_BACKUP, CONFIRM_CANCEL_RUNNING_BACKUP = range(2)


async def cancel_running_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get("running_backups", False):
            context.bot_data["running_backups"] = {}
            await update.message.reply_text(text="ليس لديك عمليات جارية ❗️")
            return ConversationHandler.END

        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{vip} -> {backup}", callback_data=f"{vip}_{backup}"
                )
            ]
            for vip, backup in context.bot_data["running_backups"].items()
        ]
        await update.message.reply_text(
            text="اختر العملية",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return RUNNING_BACKUP


async def choose_running_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        vip_channel, backup_channel = update.callback_query.data.split("_")
        context.user_data["running_backup_vip"] = vip_channel
        await update.callback_query.edit_message_text(
            text=(
                f"هل أنت متأكد من أنك تريد إلغاء نسخ جميع المنشورات من القناة:\n"
                f"<code>{vip_channel}</code>\n"
                f"إلى القناة:\n<code>{backup_channel}</code>"
            ),
            reply_markup=InlineKeyboardMarkup(
                build_confirmation_keyboard("cancel_running_backup")
            ),
        )
        return CONFIRM_CANCEL_RUNNING_BACKUP


async def confirm_cancel_running_backup(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            vip_channel = int(context.user_data["running_backup_vip"])
            del context.bot_data["running_backups"][vip_channel]
            text = "تمت العملية بنجاح ✅"
        else:
            text = "تم الإلغاء ❌"
        await update.callback_query.edit_message_text(text=text)
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(text="تم الإلغاء ❌")
        return ConversationHandler.END


cancel_running_backup_handler = ConversationHandler(
    entry_points=[
        CommandHandler(
            "cancel_backup",
            cancel_running_backup,
        )
    ],
    states={
        RUNNING_BACKUP: [
            CallbackQueryHandler(
                choose_running_backup,
                "^-?[0-9]+_-?[0-9]+$",
            )
        ],
        CONFIRM_CANCEL_RUNNING_BACKUP: [
            CallbackQueryHandler(
                confirm_cancel_running_backup,
                "^((yes)|(no)) cancel_running_backup$",
            )
        ],
    },
    fallbacks=[
        CommandHandler(
            "cancel",
            cancel,
        )
    ],
)
