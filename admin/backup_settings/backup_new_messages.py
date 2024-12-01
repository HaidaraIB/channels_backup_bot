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
        for channel in backup_channels:
            await client.send_file(
                channel.channel_id,
                gallery,
                caption=[m.text for m in gallery],
            )
            await asyncio.sleep(5)
    raise events.StopPropagation
