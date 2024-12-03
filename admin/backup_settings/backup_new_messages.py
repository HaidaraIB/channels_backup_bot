from telethon import events
from telethon.tl.patched import Message
from TeleClientSingleton import TeleClientSingleton
import models
import asyncio


async def backup_message(event: events.NewMessage.Event | events.Album.Event):

    backup_channels = models.BackupChannel.get_by(from_channel_id=event.chat_id)
    if not backup_channels:
        return

    gallery = getattr(event, "messages", None)
    if event.grouped_id and not gallery:
        return

    client = TeleClientSingleton().client

    # Handle Single Media
    if not event.grouped_id:
        message: Message = event.message
        for text_need_to_change in models.TextNeedToChange.get():
            if message.text:
                message.text = message.text.replace(
                    text_need_to_change.change_from, text_need_to_change.change_to
                )
        # Single Photo
        if message.photo or message.video:
            for channel in backup_channels:
                await client.send_file(
                    channel.channel_id,
                    caption=message.text,
                    file=message.photo if message.photo else message.video,
                )
                await asyncio.sleep(5)

        # Just Text
        else:
            for channel in backup_channels:
                await client.send_message(
                    channel.channel_id,
                    message.text,
                )
                await asyncio.sleep(5)
    # Albums
    else:
        caption = [""]
        for message in gallery:
            for text_need_to_change in models.TextNeedToChange.get():
                if message.text:
                    message.text = message.text.replace(
                        text_need_to_change.change_from, text_need_to_change.change_to
                    )
                caption.append(message.text)

        for channel in backup_channels:
            await client.send_file(
                channel.channel_id,
                gallery,
                caption=caption,
            )
            await asyncio.sleep(5)
    raise events.StopPropagation
