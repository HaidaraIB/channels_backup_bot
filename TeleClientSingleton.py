import os
from telethon import TelegramClient


class TeleClientSingleton(TelegramClient):
    client = None
    # bot = None

    def __new__(cls, *args, **kwargs):
        # if not cls.bot:
        #     cls.bot = TelegramClient(
        #         session="telethon_bot_session",
        #         api_id=int(os.getenv("API_ID")),
        #         api_hash=os.getenv("API_HASH"),
        #     ).start(
        #         bot_token=os.getenv("BOT_TOKEN"),
        #     )
        if not cls.client:
            cls.client = TelegramClient(
                session="telethon_client_session",
                api_id=int(os.getenv("API_ID")),
                api_hash=os.getenv("API_HASH"),
            ).start(
                phone=os.getenv("PHONE"),
            )

        return cls

    @classmethod
    def disconnect_all(cls):
        # cls.bot.disconnect()
        cls.client.disconnect()