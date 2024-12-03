from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from custom_filters import Admin
from admin.backup_settings.common import (
    set_backup_channel_commands,
    set_vip_channel_commands,
    build_channels_keyboard,
    perform_backup,
)
from common.keyboards import build_confirmation_keyboard
from start import admin_command
import asyncio

VIP_CHANNEL, BACKUP_CHANNEL, CONFIRM_BACKUP, CONFIRM_CANCEL_BACKUP = range(4)


async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get("running_backups", False):
            context.bot_data["running_backups"] = {}
        keyboard = build_channels_keyboard(
            [
                context.bot_data[channel]
                for channel in set_vip_channel_commands
                if context.bot_data.get(channel, False)
            ]
        )
        await update.message.reply_text(
            text="اختر قناة VIP",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return VIP_CHANNEL


async def choose_vip_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        vip_channel = int(update.callback_query.data)
        context.user_data["backup_vip_channel"] = vip_channel
        keyboard = build_channels_keyboard(
            [
                context.bot_data[channel]
                for channel in set_backup_channel_commands
                if context.bot_data.get(channel, False)
            ]
        )
        await update.callback_query.edit_message_text(
            text="اختر قناة Backup",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return BACKUP_CHANNEL


async def choose_backup_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        backup_channel = int(update.callback_query.data)
        context.user_data["backup_backup_channel"] = backup_channel
        vip_channel = context.user_data["backup_vip_channel"]
        if (
            context.bot_data["running_backups"].get(vip_channel, False)
            == backup_channel
        ):

            await update.callback_query.edit_message_text(
                text="هناك عملية نسخ جارية بالفعل بين القناتين، هل تريد إلغاءها؟",
                reply_markup=InlineKeyboardMarkup(
                    build_confirmation_keyboard("cancel_backup")
                ),
            )
            return CONFIRM_CANCEL_BACKUP

        await update.callback_query.edit_message_text(
            text=(
                f"هل أنت متأكد من أنك تريد نسخ جميع المنشورات من القناة:\n"
                f"<code>{vip_channel}</code>\n"
                f"إلى القناة:\n<code>{backup_channel}</code>"
            ),
            reply_markup=InlineKeyboardMarkup(build_confirmation_keyboard("backup")),
        )
        return CONFIRM_BACKUP


async def confirm_cancel_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            vip_channel = context.user_data["backup_vip_channel"]
            del context.bot_data["running_backups"][vip_channel]
            text = "تمت العملية بنجاح ✅"
        else:
            text = "تم الإلغاء ❌"
        await update.callback_query.edit_message_text(text=text)
        return ConversationHandler.END


async def confirm_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            vip_channel = context.user_data["backup_vip_channel"]
            backup_channel = context.user_data["backup_backup_channel"]
            context.bot_data["running_backups"][vip_channel] = backup_channel
            asyncio.create_task(
                perform_backup(
                    vip_channel=vip_channel,
                    backup_channel=backup_channel,
                    context=context,
                    admin_id=update.effective_user.id,
                )
            )
            text = "عملية النسخ جارية الآن 🔃"
        else:
            text = "تم الإلغاء ❌"
        await update.callback_query.edit_message_text(text=text)
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.message.reply_text(text="تم الإلغاء ❌")
        return ConversationHandler.END


start_backup_command = CommandHandler(
    "start_backup",
    backup,
)
backup_handler = ConversationHandler(
    entry_points=[start_backup_command],
    states={
        VIP_CHANNEL: [
            CallbackQueryHandler(
                choose_vip_channel,
                "^-?[0-9]+$",
            ),
        ],
        BACKUP_CHANNEL: [
            CallbackQueryHandler(
                choose_backup_channel,
                "^-?[0-9]+$",
            ),
        ],
        CONFIRM_BACKUP: [
            CallbackQueryHandler(
                confirm_backup,
                "^((yes)|(no)) backup$",
            )
        ],
        CONFIRM_CANCEL_BACKUP: [
            CallbackQueryHandler(
                confirm_cancel_backup,
                "^((yes)|(no)) cancel_backup$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        start_backup_command,
        CommandHandler(
            "cancel",
            cancel,
        ),
    ],
)
