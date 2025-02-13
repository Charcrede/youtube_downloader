import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DownloadProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "download_progress"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def send_progress(self, event):
        await self.send(text_data=json.dumps({"progress": event["progress"]}))
