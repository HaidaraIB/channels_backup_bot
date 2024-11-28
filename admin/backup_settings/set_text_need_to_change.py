from telegram import Update, Chat
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin


ORIGINAL, REPLACE = range(2)


async def set_text_need_to_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get("texts_need_to_change", False):
            context.bot_data["texts_need_to_change"] = {}
        await update.message.reply_text(text="حسناً، أرسل النص الأصلي")
        return ORIGINAL


async def get_original(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.user_data["original_text_to_change"] = update.message.text
        await update.message.reply_text(text="الآن النص البديل")
        return REPLACE


async def get_replace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        origianl_text = context.user_data["original_text_to_change"]
        context.bot_data["texts_need_to_change"][origianl_text] = update.message.text
        await update.message.reply_text(text="تمت العملية بنجاح ✅")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.message.reply_text(text="تم الإلغاء ❌")
        return ConversationHandler.END


set_text_need_to_change_handler = ConversationHandler(
    entry_points=[
        CommandHandler(
            "set_text_need_to_change",
            set_text_need_to_change,
        ),
    ],
    states={
        ORIGINAL: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_original,
            )
        ],
        REPLACE: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_replace,
            )
        ],
    },
    fallbacks=[
        CommandHandler(
            "cancel",
            cancel,
        ),
    ],
)
