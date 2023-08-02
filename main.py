from pyrogram import Client, filters
import logging
import settings

class Mirror:
    def __init__(self):
        self.api_id = settings.apiid
        self.api_hash = settings.apihash
        self.app = Client("my_session", api_id=self.api_id, api_hash=self.api_hash)
        self.channel_mappings = self.read_channel_mappings()

    def read_channel_mappings(self):
        channel_mappings = {}
        with open(settings.channels_file_path, "r") as file:
            for line in file:
                source_channel_id, destination_channel_id = map(int, line.strip().split())
                channel_mappings[source_channel_id] = destination_channel_id
        return channel_mappings

    async def forward_media_message(self, destination_channel_id, message):
        try:
            copied_message = await self.app.copy_message(
                chat_id=destination_channel_id,
                from_chat_id=message.chat.id,
                message_id=message.id,
            )
        except Exception as e:
            logging.error(f"Failed to duplicate media message: {e}")

    def run(self):
        @self.app.on_message(filters.channel)
        async def handle_message(client, message):
            chat_id = message.chat.id
            if chat_id in self.channel_mappings:
                destination_channel_id = self.channel_mappings[chat_id]

                if message.photo or message.video or message.audio or message.document:
                    await self.forward_media_message(destination_channel_id, message)
                else:
                    try:
                        copied_message = await self.app.copy_message(
                            chat_id=destination_channel_id,
                            from_chat_id=chat_id,
                            message_id=message.id,
                        )
                    except Exception as e:
                        logging.error(f"Failed to duplicate or edit message: {e}")

        self.app.run()

if __name__ == "__main__":
    media_forwarder = Mirror()
    media_forwarder.run()
