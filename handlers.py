from telegram import Update
from telegram.ext import CallbackQueryHandler, InvalidCallbackData
from telethon import events
from start import start_command, admin_command
from common.common import invalid_callback_data, create_folders
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)
from common.error_handler import error_handler
from common.force_join import check_joined_handler

from admin.backup_settings.backup_new_messages import backup_message

from TeleClientSingleton import TeleClientSingleton

from user.user_calls import *

from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *
from admin.backup_settings import *

from models import create_tables

from MyApp import MyApp


def main():
    create_folders()
    create_tables()

    app = MyApp.build_app()

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )
    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(check_joined_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(backup_handler)
    app.add_handler(set_channel_commands)
    app.add_handler(show_channels_command)
    app.add_handler(cancel_running_backup_handler)
    app.add_handler(set_text_need_to_change_handler)
    app.add_handler(show_texts_need_to_change_command)

    app.add_handler(admin_command)
    app.add_handler(start_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    tele_client = TeleClientSingleton()

    tele_client.client.add_event_handler(
        callback=backup_message,
        event=events.NewMessage,
    )
    tele_client.client.add_event_handler(
        callback=backup_message,
        event=events.Album,
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

    tele_client.disconnect_all()
