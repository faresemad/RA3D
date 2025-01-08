import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f"notifications_{self.user.id}"

        await self.join_room()
        logger.info(f"[!] NOTIFICATION -> User {self.user.id} connected to notifications websocket")

    async def disconnect(self, close_code):
        await self.leave_room()
        logger.info(f"[!] NOTIFICATION -> User {self.user.id} disconnected from notifications websocket")

    async def receive(self, text_data):
        logger.debug(f"[!] NOTIFICATION -> Received message from user {self.user.id}: {text_data}")
        pass

    async def send_notification(self, event):
        notification = event["notification"]
        await self.send_notification_to_websocket(notification)
        logger.info(f"[!] NOTIFICATION -> Sent notification to user {self.user.id}: {notification['message']}")

    async def join_room(self):
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def leave_room(self):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_notification_to_websocket(self, notification):
        await self.send(
            text_data=json.dumps(
                {
                    "message": notification["message"],
                    "created_at": notification["created_at"],
                    "is_read": notification["is_read"],
                }
            )
        )
